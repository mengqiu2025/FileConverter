# 轻转 - 文件格式转换器

个人使用的 Windows 10/11 x64 本地便携式文件格式转换器。

## 功能

- 文档/表格/PDF
- 图片
- 音频/视频
- 压缩包
- 拖入文件、批量转换、单独修改目标格式
- 默认输出到源文件旁的 `converted/`，同名自动重命名，不覆盖原文件
- 支持暂停、取消、并行设置
- 完全离线，不调用在线转换 API

## 使用

1. 进入 `dist/FileConverter`
2. 双击 `FileConverter.exe`
3. 拖入文件，选择目标格式，点击“开始转换”

## 构建

```powershell
.\build.ps1
```

构建前需安装 [requirements.txt](requirements.txt) 中的依赖，并将 FFmpeg、7-Zip 工具放入 `downd-tools`。

## 目录

```text
src/               源码
tests/             测试
downd-tools/       下载的外部工具与 Python wheel
dist/FileConverter 便携版输出
build.ps1          构建脚本
```
