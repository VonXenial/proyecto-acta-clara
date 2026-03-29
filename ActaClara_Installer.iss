[Setup]
AppName=ActaClara Pro
AppVersion=1.4
AppPublisher=VonXenial
AppPublisherURL=https://github.com/VonXenial/proyecto-acta-clara
DefaultDirName={pf64}\ActaClara
DefaultGroupName=ActaClara
DisableProgramGroupPage=yes
OutputBaseFilename=ActaClara_Setup_v1.4
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\logo\logo_icon_64px.ico
UninstallDisplayIcon={app}\ActaClara.exe
; Forzar instalación en Program Files de 64 bits (no x86)
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
; El acceso directo al escritorio se crea por defecto (sin Flags: unchecked)
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\ActaClara\ActaClara.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ActaClara\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Modelo Whisper para operación offline (sin internet):
Source: "dist\ActaClara\modelo_whisper\*"; DestDir: "{app}\modelo_whisper"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Icono leído directamente del exe embebido (índice 0) para evitar icon en blanco
Name: "{autoprograms}\ActaClara"; Filename: "{app}\ActaClara.exe"; IconFilename: "{app}\ActaClara.exe"; IconIndex: 0
Name: "{autodesktop}\ActaClara"; Filename: "{app}\ActaClara.exe"; Tasks: desktopicon; IconFilename: "{app}\ActaClara.exe"; IconIndex: 0

[Run]
Filename: "{app}\ActaClara.exe"; Description: "{cm:LaunchProgram,ActaClara}"; Flags: nowait postinstall skipifsilent
