#define MyAppName "MARVIN"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "FelipeMio"
#define MyAppExeName "MARVIN.exe"

[Setup]
AppId=MARVIN.AssistenteVirtual
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

VersionInfoVersion=0.1.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=MARVIN - Assistente Virtual
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

SetupIconFile=..\assets\marvin\marvin.ico

DefaultDirName={localappdata}\Programs\MARVIN
DefaultGroupName=MARVIN

PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible

OutputDir=..\release
OutputBaseFilename=MARVIN-Setup

Compression=lzma2
SolidCompression=yes

WizardStyle=modern
DisableProgramGroupPage=yes

UninstallDisplayIcon={app}\{#MyAppExeName}

CloseApplications=yes
RestartApplications=no


[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked


[Files]
Source: "..\dist\MARVIN\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{autoprograms}\MARVIN"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

Name: "{autodesktop}\MARVIN"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon


[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir MARVIN"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent

