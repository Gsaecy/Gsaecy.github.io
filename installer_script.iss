; Safevaultg Windows 安装程序脚本 (Inno Setup)
; 用于创建EXE安装程序以符合Microsoft合作伙伴中心要求

[Setup]
; 基本设置
AppName=Safevaultg
AppVersion=1.0.0
AppPublisher=Your Company Name
AppPublisherURL=https://safevault-service.online
AppSupportURL=https://safevault-service.online/support
AppUpdatesURL=https://safevault-service.online/updates
DefaultDirName={pf}\Safevaultg
DefaultGroupName=Safevaultg
Compression=lzma2
SolidCompression=yes
OutputDir=.\Output
OutputBaseFilename=Safevaultg_Setup
SetupIconFile=.\Resources\app.ico
UninstallDisplayIcon={app}\Safevaultg.exe
LicenseFile=.\Resources\license.txt
InfoBeforeFile=.\Resources\readme.txt
WizardStyle=modern

; 安装程序签名信息（需要代码签名证书）
; SignTool=mysigntool $f
; SignedUninstaller=yes

; 架构设置
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
; 主应用程序文件
Source: ".\Application\Safevaultg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\Application\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\Application\*.config"; DestDir: "{app}"; Flags: ignoreversion

; 运行时依赖（如果需要）
; Source: ".\Dependencies\vcredist_x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
; Source: ".\Dependencies\dotnet48.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

; 文档文件
Source: ".\Documentation\*"; DestDir: "{app}\Documentation"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Safevaultg"; Filename: "{app}\Safevaultg.exe"
Name: "{group}\{cm:UninstallProgram,Safevaultg}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Safevaultg"; Filename: "{app}\Safevaultg.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Safevaultg"; Filename: "{app}\Safevaultg.exe"; Tasks: quicklaunchicon

[Run]
; 安装后运行主程序（可选）
; Filename: "{app}\Safevaultg.exe"; Description: "{cm:LaunchProgram,Safevaultg}"; Flags: nowait postinstall skipifsilent

; 安装运行时依赖（如果需要）
; Filename: "{tmp}\vcredist_x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installing Visual C++ Redistributable..."; Check: VCRedistNeedsInstall
; Filename: "{tmp}\dotnet48.exe"; Parameters: "/q /norestart"; StatusMsg: "Installing .NET Framework 4.8..."; Check: DotNetNeedsInstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}\Logs"
Type: filesandordirs; Name: "{app}\Temp"

[Code]
// 自定义函数：检查系统要求
function InitializeSetup(): Boolean;
begin
  // 检查Windows版本（需要Windows 10或更高版本）
  if GetWindowsVersion < $0A000000 then // Windows 10 = 10.0
  begin
    MsgBox('This application requires Windows 10 or later.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // 检查管理员权限
  if not IsAdminLoggedOn then
  begin
    MsgBox('Administrator privileges are required to install this application.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // 检查磁盘空间（至少需要100MB）
  if DirSpace(ExpandConstant('{sd}')) < 104857600 then // 100MB in bytes
  begin
    MsgBox('Insufficient disk space. Please free up at least 100MB of space.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  Result := True;
end;

// 检查VC++ Redistributable是否已安装
function VCRedistNeedsInstall(): Boolean;
begin
  // 这里添加检查VC++ Redistributable的逻辑
  // 如果未安装返回True，已安装返回False
  Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64');
end;

// 检查.NET Framework是否已安装
function DotNetNeedsInstall(): Boolean;
begin
  // 这里添加检查.NET Framework 4.8的逻辑
  Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full');
end;

// 安装完成后的处理
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 安装完成后的操作
    // 例如：创建配置文件、注册服务等
  end;
end;

// 卸载前的处理
function InitializeUninstall(): Boolean;
begin
  // 检查应用程序是否正在运行
  if CheckForMutexes('SafevaultgMutex') then
  begin
    MsgBox('Please close Safevaultg before uninstalling.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  Result := True;
end;