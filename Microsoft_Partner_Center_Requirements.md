# Microsoft合作伙伴中心发布要求 - Safevaultg Windows

## 任务1：Windows版本下载格式更改

### 当前状态
- 当前提供：ZIP压缩包下载
- 需要更改为：EXE安装程序

### 需要完成的工作：

#### 1. 创建EXE安装程序
- 使用合适的安装程序工具（如Inno Setup、NSIS、WiX Toolset）
- 包含所有必要的运行时依赖
- 添加数字签名（用于Microsoft合作伙伴中心验证）

#### 2. 安装程序功能要求
- 静默安装支持（/SILENT或/VERYSILENT参数）
- 自定义安装路径选项
- 创建开始菜单快捷方式
- 创建桌面快捷方式（可选）
- 添加/删除程序条目
- 支持升级安装

#### 3. 安装程序返回代码
安装程序必须返回标准的Windows安装程序退出代码：
- 0：成功安装
- 1：一般错误
- 2：无效参数
- 3：文件复制失败
- 4：磁盘空间不足
- 5：用户取消
- 6：需要管理员权限
- 7：系统要求不满足
- 8：需要重启
- 9：版本冲突
- 10：数字签名验证失败

## 任务2：EXE返回代码文档

### 文档URL要求
Microsoft合作伙伴中心需要提供所有杂项EXE返回代码值的文档URL。这包括：

#### 1. 主应用程序返回代码
```
https://docs.safevault-service.online/error-codes
```

#### 2. 安装程序返回代码
```
https://docs.safevault-service.online/installer-error-codes
```

#### 3. 卸载程序返回代码
```
https://docs.safevault-service.online/uninstaller-error-codes
```

#### 4. 服务/守护进程返回代码
```
https://docs.safevault-service.online/service-error-codes
```

### 需要创建的文档内容

#### 安装程序错误代码文档示例：
```markdown
# Safevaultg Windows 安装程序错误代码

## 标准返回代码
- **0**: 安装成功完成
- **1**: 一般安装错误
- **2**: 无效的命令行参数
- **3**: 文件复制失败（检查磁盘权限）
- **4**: 磁盘空间不足（需要至少 100MB 可用空间）
- **5**: 用户取消了安装
- **6**: 需要管理员权限运行
- **7**: 系统要求不满足（需要 Windows 10 1809 或更高版本）
- **8**: 需要重启系统才能完成安装
- **9**: 检测到旧版本冲突
- **10**: 数字签名验证失败

## 自定义返回代码（100+）
- **101**: .NET Framework 4.8 未安装
- **102**: Visual C++ 运行时库缺失
- **103**: 防病毒软件阻止安装
- **104**: 网络连接检查失败
- **105**: 许可证验证失败
```

#### 应用程序错误代码文档示例：
```markdown
# Safevaultg Windows 应用程序错误代码

## 启动错误（1000-1999）
- **1001**: 配置文件损坏
- **1002**: 数据库连接失败
- **1003**: 许可证过期
- **1004**: 硬件不兼容

## 运行时错误（2000-2999）
- **2001**: 内存不足
- **2002**: 磁盘写入失败
- **2003**: 网络连接丢失
- **2004**: 加密操作失败

## 服务错误（3000-3999）
- **3001**: 服务启动失败
- **3002**: 服务权限不足
- **3003**: 服务依赖项未启动
```

## 实施步骤

### 步骤1：创建EXE安装程序
1. 选择合适的安装程序框架
2. 配置安装脚本
3. 添加数字签名
4. 测试安装/卸载流程
5. 验证返回代码

### 步骤2：创建错误代码文档
1. 在网站上创建 `/error-codes` 页面
2. 在网站上创建 `/installer-error-codes` 页面
3. 在网站上创建 `/uninstaller-error-codes` 页面
4. 确保文档可公开访问
5. 测试URL可访问性

### 步骤3：更新下载链接
1. 将网站上的ZIP下载链接替换为EXE
2. 更新版本信息
3. 添加安装说明
4. 提供备用下载方式（如微软商店）

## Microsoft合作伙伴中心提交检查清单

- [ ] EXE安装程序已创建并测试
- [ ] 安装程序有有效的数字签名
- [ ] 所有返回代码文档URL已创建
- [ ] 文档URL可公开访问
- [ ] 安装说明清晰完整
- [ ] 系统要求文档已更新
- [ ] 隐私政策链接有效
- [ ] 支持联系方式已提供
- [ ] 应用程序截图已更新
- [ ] 版本号符合规范

## 有用的资源

1. [Microsoft合作伙伴中心文档](https://docs.microsoft.com/partner-center/)
2. [Windows应用程序认证工具包](https://docs.microsoft.com/windows/uwp/debug-test-perf/windows-app-certification-kit)
3. [代码签名证书获取](https://docs.microsoft.com/windows-hardware/drivers/dashboard/get-a-code-signing-certificate)
4. [应用程序包要求](https://docs.microsoft.com/windows/uwp/publish/app-package-requirements)
```

如果你能提供：
1. 当前ZIP文件的结构和内容
2. 应用程序的具体功能和要求
3. 现有的错误代码定义

我可以帮你创建更具体的安装脚本和文档。另外，你需要获取代码签名证书来为EXE文件签名，这是Microsoft合作伙伴中心的要求。