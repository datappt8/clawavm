; ClawAVM Windows 安装程序脚本 (Inno Setup)
; 生成专业的 Windows 安装包

#define MyAppName "ClawAVM"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "datappt8"
#define MyAppURL "https://github.com/datappt8/clawavm"
#define MyAppExeName "ClawAVM.exe"

[Setup]
AppId={{F8A3B4C5-D6E7-8901-2345-6789ABCDEF01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\ClawAVM
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=ClawAVM-Setup-{#MyAppVersion}
SetupIconFile=assets\clawavm.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\banner.svg"; DestDir: "{app}\assets"; Flags: ignoreversion

[Dirs]
Name: "{localappdata}\ClawAVM"; Permissions: everyone-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  // 检查系统要求
  if not IsDotNetInstalled(net40, 0) then begin
    MsgBox('需要 .NET Framework 4.0 或更高版本。', mbError, MB_OK);
    Result := false;
  end else begin
    Result := true;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    // 创建数据目录
    CreateDir(ExpandConstant('{localappdata}\ClawAVM\workspace'));
  end;
end;
