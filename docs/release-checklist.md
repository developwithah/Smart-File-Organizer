# Version 3.0 Release and Regression Checklist

Use this checklist before creating the `v3.0.0` Git tag and GitHub Release.

## Source and metadata

- [ ] Working tree is clean and all intended changes are committed.
- [ ] `config.py` displays `Version 3.0` in the application.
- [ ] Release tag is exactly `v3.0.0`.
- [ ] README, CHANGELOG, installer metadata, and release notes state Version 3.0 consistently.
- [ ] MIT LICENSE is present and linked from README.
- [ ] Real icon is present at `assets/smart-file-organizer.ico`.
- [ ] README renders all six real Windows screenshots with captions.

## Startup and navigation

- [ ] Application starts from Python source.
- [ ] Application starts from the packaged executable.
- [ ] Application icon appears in the Windows title bar, executable, and installer.
- [ ] File, Tools, and Help menus open and invoke the correct commands.
- [ ] Toolbar actions work: Browse, Organize, Undo, Duplicates, and Storage.
- [ ] Keyboard shortcuts work: Ctrl+O, Ctrl+D, Ctrl+S, Ctrl+Z, and F1.
- [ ] About and Version Information display Version 3.0.
- [ ] Window resizes and maximizes without clipping toolbar, dashboard, progress area, or status bar.

## Folder selection and empty state

- [ ] Browse Folder selects a valid directory and updates the dashboard.
- [ ] Dragging a valid folder updates the folder field and dashboard.
- [ ] Dropping a file shows the friendly folder-required message.
- [ ] Dropping multiple items shows the one-folder-at-a-time message.
- [ ] The no-folder state keeps Organize, Duplicate Finder, and Storage Analyzer unavailable.
- [ ] Browse remains available with no selected folder.

## File organization and undo

- [ ] Organize categorizes supported top-level files correctly.
- [ ] Unknown extensions remain untouched.
- [ ] Destination folders are created as needed.
- [ ] Existing destination files are not overwritten.
- [ ] Progress, status, and organized-file counter update while processing.
- [ ] The GUI remains responsive during a large organization operation.
- [ ] Organize failure shows an error and restores action availability.
- [ ] Undo remains disabled before a successful move operation.
- [ ] Undo restores moved files in reverse order.
- [ ] Undo progress updates without freezing the GUI.
- [ ] Missing/conflicting files are reported as skipped without crashing.
- [ ] Undo disables after a fully successful restore and remains available after a partial restore.

## Duplicate Finder

- [ ] Scan recurses through nested folders.
- [ ] Identical content with different names is detected as duplicate.
- [ ] Same-size files with different content are not reported as duplicate.
- [ ] Duplicate scan progress updates without freezing the GUI.
- [ ] Results are sorted by duplicate count, then recoverable space.
- [ ] Results window is read-only and no duplicate files are moved or deleted.
- [ ] Dashboard Duplicate Groups updates after a successful scan.
- [ ] No-duplicate folders show the expected completion message.

## Storage Analyzer

- [ ] Analysis recurses through nested folders.
- [ ] Total file count, folder count, and byte total are correct.
- [ ] Images, Videos, Documents, Music, Archives, and Others are categorized correctly.
- [ ] Largest files and largest folders are correct.
- [ ] Displayed KB/MB/GB/TB values are formatted correctly.
- [ ] Analysis progress updates without freezing the GUI.
- [ ] Results window is read-only and does not alter files.
- [ ] Dashboard Total Files and Total Size update after successful analysis.

## Packaging and installer

- [ ] `python -m pip install -r requirements-build.txt` succeeds in a clean environment.
- [ ] `./packaging/build-windows.ps1 -RequireIcon` removes old output and creates `dist/SmartFileOrganizer.exe`.
- [ ] The executable launches on a Windows test machine without Python installed.
- [ ] Inno Setup compiles `installer/SmartFileOrganizer.iss`.
- [ ] Installer creates Start Menu and optional desktop shortcuts.
- [ ] Installed application launches and uninstalls cleanly.

## GitHub Release

- [ ] Create annotated tag `v3.0.0` on the verified release commit.
- [ ] Create GitHub Release titled `Smart File Organizer v3.0.0`.
- [ ] Attach tested standalone executable and installer assets.
- [ ] Paste Version 3.0 changelog notes into the release description.
- [ ] Confirm build artifacts are not committed to Git.
