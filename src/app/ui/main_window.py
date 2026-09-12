import os
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES

from app.core.config import load_config, save_config
from app.core.engines import EngineNotFoundError
from app.core.job_queue import JobQueue
from app.core.logger import cleanup_old_logs, configure_logging
from app.core.service import ConverterService
from app.core.ui_model import build_file_item
from app.ui.settings_dialog import SettingsDialog


CATEGORY_LABELS = {
    "document": "文档",
    "image": "图片",
    "audio": "音频",
    "video": "视频",
    "archive": "压缩包",
}

CATEGORY_TARGETS = {
    "document": ["pdf", "docx", "txt", "md", "html", "csv", "xlsx"],
    "image": ["png", "jpg", "bmp", "gif", "tif", "webp", "ico", "pdf"],
    "audio": ["mp3", "wav", "flac", "aac", "m4a", "ogg", "opus"],
    "video": ["mp4", "mkv", "webm", "mp3", "wav", "aac", "m4a"],
    "archive": ["zip", "7z", "tar", "gz", "bz2", "xz"],
}


class ConverterApp:
    def __init__(self, root, app_dir):
        self.root = root
        self.app_dir = Path(app_dir)
        self.config_path = self.app_dir / "config.json"
        self.config = load_config(self.config_path)
        self.logger = configure_logging(self.app_dir)
        self.service = ConverterService(self.app_dir, self.config_path)
        self.items = {}
        self.custom_targets = {}
        self.queue = None
        self.run_thread = None

        self.root.title("轻转 - 文件格式转换器")
        self.root.geometry("980x640")
        self.root.minsize(820, 520)

        self._build_ui()
        self._refresh_engine_status()

    def _build_ui(self):
        root = ttk.Frame(self.root, padding=10)
        root.pack(fill="both", expand=True)

        top = ttk.LabelFrame(root, text="批量默认目标", padding=8)
        top.pack(fill="x")
        self.default_vars = {}
        for column, category in enumerate(CATEGORY_LABELS):
            ttk.Label(top, text=CATEGORY_LABELS[category]).grid(
                row=0, column=column, padx=(0, 4), sticky="w"
            )
            variable = tk.StringVar(value=self.config["defaults"][category])
            combo = ttk.Combobox(
                top,
                textvariable=variable,
                values=CATEGORY_TARGETS[category],
                state="readonly",
                width=10,
            )
            combo.grid(row=1, column=column, padx=(0, 12), sticky="w")
            combo.bind(
                "<<ComboboxSelected>>",
                lambda _event, cat=category: self._on_default_changed(cat),
            )
            self.default_vars[category] = variable

        self.engine_label = ttk.Label(root, text="外部引擎状态：检查中...")
        self.engine_label.pack(anchor="w", pady=(8, 0))

        list_frame = ttk.LabelFrame(root, text="文件列表", padding=8)
        list_frame.pack(fill="both", expand=True, pady=8)
        columns = ("source", "category", "target", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        self.tree.heading("source", text="文件")
        self.tree.heading("category", text="类别")
        self.tree.heading("target", text="目标格式")
        self.tree.heading("status", text="状态")
        self.tree.column("source", width=480, anchor="w")
        self.tree.column("category", width=90, anchor="center")
        self.tree.column("target", width=90, anchor="center")
        self.tree.column("status", width=150, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.tag_configure("unavailable", foreground="#c62828")
        self.tree.tag_configure("success", foreground="#2e7d32")
        self.tree.tag_configure("failed", foreground="#c62828")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        selected_frame = ttk.Frame(root)
        selected_frame.pack(fill="x")
        ttk.Label(selected_frame, text="选中文件目标：").pack(side="left")
        self.selected_target_var = tk.StringVar()
        self.selected_target_combo = ttk.Combobox(
            selected_frame,
            textvariable=self.selected_target_var,
            state="readonly",
            width=12,
        )
        self.selected_target_combo.pack(side="left", padx=4)
        self.selected_target_combo.bind("<<ComboboxSelected>>", self._on_target_selected)

        action_frame = ttk.Frame(root)
        action_frame.pack(fill="x", pady=(10, 0))
        self.add_button = ttk.Button(action_frame, text="添加文件", command=self._add_files_dialog)
        self.add_button.pack(side="left")
        self.clear_button = ttk.Button(action_frame, text="清空列表", command=self._clear_items)
        self.clear_button.pack(side="left", padx=6)
        self.convert_button = ttk.Button(
            action_frame, text="开始转换", command=self._start_conversion
        )
        self.convert_button.pack(side="left", padx=6)
        self.pause_button = ttk.Button(action_frame, text="暂停", command=self._pause)
        self.pause_button.pack(side="left", padx=6)
        self.cancel_button = ttk.Button(action_frame, text="取消", command=self._cancel)
        self.cancel_button.pack(side="left", padx=6)
        self.settings_button = ttk.Button(action_frame, text="设置", command=self._open_settings)
        self.settings_button.pack(side="right")

        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", pady=(10, 4))
        self.status_label = ttk.Label(root, text="拖入文件或点击“添加文件”")
        self.status_label.pack(anchor="w")

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event):
        paths = self._parse_drop_data(event.data)
        self._add_paths(paths)

    def _parse_drop_data(self, data):
        if isinstance(data, (list, tuple)):
            return [Path(item) for item in data]
        try:
            return [Path(item) for item in self.root.tk.splitlist(data)]
        except tk.TclError:
            return [Path(part) for part in str(data).split() if part]

    def _add_files_dialog(self):
        paths = filedialog.askopenfilenames(title="选择文件")
        if paths:
            self._add_paths([Path(path) for path in paths])

    def _add_paths(self, paths):
        added = 0
        libreoffice_available = self._libreoffice_available()
        for raw_path in paths:
            path = Path(raw_path)
            if not path.is_file():
                continue
            try:
                item = build_file_item(
                    path,
                    self.config,
                    libreoffice_available=libreoffice_available,
                )
            except ValueError as exc:
                self.logger.warning("跳过 %s: %s", path, exc)
                continue

            if path in self.custom_targets:
                custom = self.custom_targets[path]
                if custom in item.supported_targets:
                    item.target_ext = custom
                    item.available = True
                    item.reason = ""

            iid = str(path)
            if iid in self.items:
                self.tree.delete(iid)
            self.tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    str(path),
                    CATEGORY_LABELS[item.category],
                    item.target_ext,
                    self._status_text(item),
                ),
                tags=self._tags(item),
            )
            self.items[iid] = item
            added += 1

        self.status_label.config(text=f"已添加 {added} 个文件")

    def _libreoffice_available(self):
        # v1 尚未实现 LibreOffice 文档引擎；即使系统存在 soffice，也不开放该转换。
        return False

    def _on_default_changed(self, category):
        value = self.default_vars[category].get()
        self.config["defaults"][category] = value
        save_config(self.config, self.config_path)
        self.service = ConverterService(self.app_dir, self.config_path)

        for iid, item in self.items.items():
            if item.path in self.custom_targets:
                continue
            item.target_ext = value
            item.available = value in item.supported_targets
            item.reason = "" if item.available else "需要可选文档引擎"
            self.tree.item(
                iid,
                values=(
                    str(item.path),
                    CATEGORY_LABELS[item.category],
                    item.target_ext,
                    self._status_text(item),
                ),
                tags=self._tags(item),
            )

    def _on_tree_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            self.selected_target_combo.config(values=[])
            self.selected_target_var.set("")
            return
        item = self.items[selected[0]]
        self.selected_target_combo.config(values=item.supported_targets)
        self.selected_target_var.set(item.target_ext)

    def _on_target_selected(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        iid = selected[0]
        item = self.items[iid]
        target = self.selected_target_var.get()
        if target not in item.supported_targets:
            return
        item.target_ext = target
        item.available = True
        item.reason = ""
        self.custom_targets[item.path] = target
        self.tree.item(
            iid,
            values=(
                str(item.path),
                CATEGORY_LABELS[item.category],
                item.target_ext,
                self._status_text(item),
            ),
            tags=self._tags(item),
        )

    def _start_conversion(self):
        available = [item for item in self.items.values() if item.available]
        if not available:
            messagebox.showwarning("没有可转换文件", "请先添加文件，并确认目标格式可用。")
            return

        save_config(self.config, self.config_path)
        self.service = ConverterService(self.app_dir, self.config_path)
        max_workers = self._max_workers()
        self.queue = JobQueue(self.service, max_workers=max_workers, on_job_finished=self._on_job_finished)
        for item in available:
            self.queue.enqueue(item.path, item.target_ext)

        self.progress.config(maximum=len(available), value=0)
        self.convert_button.config(state="disabled")
        self.add_button.config(state="disabled")
        self.clear_button.config(state="disabled")
        self.settings_button.config(state="disabled")
        self.status_label.config(text="正在转换...")
        self.run_thread = threading.Thread(target=self._run_queue, daemon=True)
        self.run_thread.start()

    def _max_workers(self):
        parallel = self.config["execution"]["parallel"]
        if not parallel:
            return 1
        workers = int(self.config["execution"]["max_workers"] or 0)
        if workers <= 0:
            workers = min(4, max(1, (os.cpu_count() or 2) // 2))
        return min(8, max(1, workers))

    def _run_queue(self):
        jobs = self.queue.run()
        self.root.after(0, lambda: self._on_queue_finished(jobs))

    def _on_job_finished(self, job):
        self.root.after(0, lambda: self._update_job_row(job))

    def _on_queue_finished(self, jobs):
        self.progress.config(value=len(jobs))
        success = sum(job.status == "success" for job in jobs)
        failed = sum(job.status == "failed" for job in jobs)
        cancelled = sum(job.status == "cancelled" for job in jobs)
        self.status_label.config(
            text=f"完成：成功 {success}，失败 {failed}，取消 {cancelled}"
        )
        self.convert_button.config(state="normal")
        self.add_button.config(state="normal")
        self.clear_button.config(state="normal")
        self.settings_button.config(state="normal")

    def _update_job_row(self, job):
        iid = str(job.source)
        item = self.items.get(iid)
        if item is None:
            return
        item.status = job.status
        item.error = job.error
        self.tree.item(
            iid,
            values=(
                str(item.path),
                CATEGORY_LABELS[item.category],
                item.target_ext,
                self._status_text(item),
            ),
            tags=self._tags(item),
        )
        self.progress.step(1)

    def _status_text(self, item):
        if item.status == "success":
            return "成功"
        if item.status == "failed":
            return f"失败：{item.error or item.reason or '未知错误'}"
        if item.status == "cancelled":
            return "已取消"
        if not item.available:
            return item.reason
        return "等待转换"

    def _tags(self, item):
        if item.status == "success":
            return ("success",)
        if item.status == "failed":
            return ("failed",)
        if not item.available:
            return ("unavailable",)
        return ()

    def _pause(self):
        if self.queue:
            if self.queue.is_paused():
                self.queue.resume()
                self.pause_button.config(text="暂停")
                self.status_label.config(text="已继续")
            else:
                self.queue.pause()
                self.pause_button.config(text="继续")
                self.status_label.config(text="已暂停")

    def _cancel(self):
        if self.queue:
            self.queue.cancel()
            self.status_label.config(text="正在取消...")

    def _clear_items(self):
        for iid in list(self.items):
            self.tree.delete(iid)
        self.items.clear()
        self.custom_targets.clear()
        self.status_label.config(text="列表已清空")

    def _open_settings(self):
        dialog = SettingsDialog(
            self.root,
            self.app_dir,
            self.config,
            on_cleanup=self._cleanup,
        )
        self.root.wait_window(dialog)
        save_config(self.config, self.config_path)
        self.service = ConverterService(self.app_dir, self.config_path)
        self._refresh_engine_status()

    def _cleanup(self):
        removed = 0
        temp_dir = self.app_dir / "temp"
        if temp_dir.exists():
            for path in temp_dir.iterdir():
                if path.is_file():
                    path.unlink()
                    removed += 1
                elif path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                    removed += 1
        log_dir = self.app_dir / "logs"
        before = set(log_dir.glob("*.log*")) if log_dir.exists() else set()
        cleanup_old_logs(log_dir, self.config["logs"]["retention_days"])
        after = set(log_dir.glob("*.log*")) if log_dir.exists() else set()
        removed += len(before - after)
        return removed

    def _refresh_engine_status(self):
        statuses = []
        for engine_name, label in (
            ("ffmpeg", "FFmpeg"),
            ("sevenzip", "7-Zip"),
            ("libreoffice", "LibreOffice"),
        ):
            try:
                path = self.service.engine_manager.resolve(engine_name)
                statuses.append(f"{label}: {path}")
            except EngineNotFoundError:
                statuses.append(f"{label}: 未找到")
        self.engine_label.config(text="外部引擎状态：" + "；".join(statuses))
