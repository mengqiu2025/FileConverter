$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dist = Join-Path $Root "dist\FileConverter"
$DownTools = Join-Path $Root "downd-tools"

if (Test-Path (Join-Path $Root "build\FileConverter")) {
    Remove-Item (Join-Path $Root "build\FileConverter") -Recurse -Force
}
if (Test-Path $Dist) {
    Remove-Item $Dist -Recurse -Force
}

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name FileConverter `
    --add-data "src\app;app" `
    "src\main.py"

$Tools = Join-Path $Dist "tools"
$FFmpegBin = Join-Path $Tools "ffmpeg\bin"
$SevenZipDir = Join-Path $Tools "sevenzip"
New-Item -ItemType Directory -Force -Path $FFmpegBin | Out-Null
New-Item -ItemType Directory -Force -Path $SevenZipDir | Out-Null

$FFmpegSource = Get-ChildItem (Join-Path $DownTools "ffmpeg") -Directory | Select-Object -First 1
Copy-Item (Join-Path $FFmpegSource.FullName "bin\ffmpeg.exe") $FFmpegBin -Force
Copy-Item (Join-Path $FFmpegSource.FullName "bin\ffprobe.exe") $FFmpegBin -Force

Copy-Item (Join-Path $DownTools "sevenzip-full\7z.exe") $SevenZipDir -Force
Copy-Item (Join-Path $DownTools "sevenzip-full\7z.dll") $SevenZipDir -Force

Write-Host "Portable build ready at $Dist"
