param(
    [switch]$RequireIcon
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BuildDirectory = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot "build"))
$DistDirectory = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot "dist"))
$IconPath = Join-Path $ProjectRoot "assets\smart-file-organizer.ico"
$ExecutablePath = Join-Path $DistDirectory "SmartFileOrganizer.exe"

foreach ($Directory in @($BuildDirectory, $DistDirectory)) {
    if (-not $Directory.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a path outside the project: $Directory"
    }

    if (Test-Path -LiteralPath $Directory) {
        Remove-Item -LiteralPath $Directory -Recurse -Force
    }
}

$PyInstallerArguments = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onefile",
    "--name", "SmartFileOrganizer",
    "--collect-all", "customtkinter",
    "--collect-all", "tkinterdnd2",
    "--distpath", $DistDirectory,
    "--workpath", $BuildDirectory,
    (Join-Path $ProjectRoot "main.py")
)

if (Test-Path -LiteralPath $IconPath) {
    $PyInstallerArguments = @(
        "--icon", $IconPath,
        "--add-data", "$IconPath;assets"
    ) + $PyInstallerArguments
}
elseif ($RequireIcon) {
    throw "Custom icon not found: $IconPath"
}
else {
    Write-Warning "Custom icon not found. Building without an executable icon."
}

& python -m PyInstaller @PyInstallerArguments
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE."
}

if (-not (Test-Path -LiteralPath $ExecutablePath)) {
    throw "Build completed without producing the expected executable: $ExecutablePath"
}

Write-Host "Build completed: $ExecutablePath"
