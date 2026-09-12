import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


class SettingsDialog(tk.Toplevel):
    def __init__(self, master, app_dir, config, on_cleanup):
        super().__init__(master)
        self.app_dir = Path(app_dir)
        self.config = config
        self.on_cleanup = on_cleanup

        self.title("设置")
        self.geometry("620x420")
        self.resizable(False, False)

        self.output_mode_var = tk.StringVar(value=config["output"]["mode"])
        self.custom_dir_var = tk.StringVar(value=config["output"].get("custom_dir") or "")
        self.parallel_var = tk.BooleanVar(value=config["execution"]["parallel"])
        self.max_workers_var = tk.IntVar(value=config["execution"]["max_workers"])
        self.ffmpeg_var = tk.StringVar(value=config["engines"].get("ffmpeg") or "")
        self.sevenzip_var = tk.StringVar(value=config["engines"].get("sevenzip") or "")
        self.libreoffice_var = tk.StringVar(value=config["engines"].get("libreoffice") or "")

        self._build()

    def _build(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="输出目录").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Combobox(
            frame,
            textvariable=self.output_mode_var,
            values=("converted", "custom"),
            state="readonly",
            width=12,
        ).grid(row=0, column=1, sticky="w")
        ttk.Entry(frame, textvariable=self.custom_dir_var, width=36).grid(
            row=0, column=2, padx=6
        )
        ttk.Button(frame, text="浏览", command=self._browse_custom_dir).grid(
            row=0, column=3
        )

        ttk.Checkbutton(frame, text="并行转换", variable=self.parallel_var).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=8
        )
        ttk.Label(frame, text="并发数").grid(row=1, column=2, sticky="e")
        ttk.Spinbox(frame, from_=1, to=8, textvariable=self.max_workers_var, width=8).grid(
            row=1, column=3, sticky="w", padx=6
        )

        ttk.Label(frame, text="外部引擎路径（留空则自动查找）").grid(
            row=2, column=0, columnspan=4, sticky="w", pady=(12, 4)
        )
        self._engine_row(frame, 3, "FFmpeg", self.ffmpeg_var, "ffmpeg.exe")
        self._engine_row(frame, 4, "7-Zip", self.sevenzip_var, "7z.exe")
        self._engine_row(frame, 5, "LibreOffice", self.libreoffice_var, "soffice.exe")

        buttons = ttk.Frame(frame)
        buttons.grid(row=6, column=0, columnspan=4, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text="清理缓存", command=self._cleanup).pack(side="left", padx=4)
        ttk.Button(buttons, text="取消", command=self.destroy).pack(side="left", padx=4)
        ttk.Button(buttons, text="保存", command=self._save).pack(side="left", padx=4)

    def _engine_row(self, parent, row, label, variable, filename):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=variable, width=46).grid(
            row=row, column=1, columnspan=2, sticky="w", padx=6
        )
        ttk.Button(
            parent,
            text="浏览",
            command=lambda: self._browse_engine(variable, filename),
        ).grid(row=row, column=3)

    def _browse_custom_dir(self):
        path = filedialog.askdirectory(initialdir=self.custom_dir_var.get() or str(self.app_dir))
        if path:
            self.custom_dir_var.set(path)

    def _browse_engine(self, variable, filename):
        path = filedialog.askopenfilename(
            title=f"选择 {filename}",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if path:
            variable.set(path)

    def _save(self):
        self.config["output"]["mode"] = self.output_mode_var.get()
        custom_dir = self.custom_dir_var.get().strip()
        self.config["output"]["custom_dir"] = custom_dir or None
        self.config["execution"]["parallel"] = self.parallel_var.get()
        self.config["execution"]["max_workers"] = max(0, min(8, int(self.max_workers_var.get() or 0)))
        self.config["engines"]["ffmpeg"] = self.ffmpeg_var.get().strip() or None
        self.config["engines"]["sevenzip"] = self.sevenzip_var.get().strip() or None
        self.config["engines"]["libreoffice"] = self.libreoffice_var.get().strip() or None
        self.destroy()

    def _cleanup(self):
        removed = self.on_cleanup()
        messagebox.showinfo("清理完成", f"已清理 {removed} 个文件。")
