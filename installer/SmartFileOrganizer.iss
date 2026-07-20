#define AppName "Smart File Organizer"
#define AppVersion "3.0"
#define AppPublisher "Aleeza Haseeb"
#define AppExeName "SmartFileOrganizer.exe"

[Setup]
AppId={{D0E0B3A5-6D43-4BF7-B67A-14CD3B829CC7}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=output
OutputBaseFilename=SmartFileOrganizer-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\smart-file-organizer.ico
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"
