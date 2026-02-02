# Figma 设计模板配置指南

## 🎨 模板创建步骤

### 1. 在Figma中创建模板文件
1. 登录 Figma (https://www.figma.com)
2. 创建新文件：`AI-Blog-Templates`
3. 创建以下页面（Pages）：
   - `公众号文章模板`
   - `小红书笔记模板`
   - `微博长图模板`
   - `知乎回答模板`
   - `Twitter卡片模板`

### 2. 设计模板规范

#### 公众号文章模板
- **尺寸**: 900px × 任意高度（建议不超过5000px）
- **关键元素**:
  - 标题区域（大字体，醒目）
  - 作者/日期信息
  - 正文区域（可多列）
  - 图片占位符
  - 二维码/关注引导区域
- **节点命名规范**:
  - `title` - 标题
  - `author` - 作者
  - `date` - 日期
  - `content` - 正文内容
  - `cover_image` - 封面图
  - `summary` - 摘要

#### 小红书笔记模板
- **尺寸**: 1242px × 1660px（竖屏）
- **关键元素**:
  - 封面大图区域
  - 标题（吸引眼球）
  - 正文（分段清晰，emoji点缀）
  - 标签区域
  - 个人品牌信息
- **节点命名规范**:
  - `cover` - 封面图
  - `title` - 标题
  - `content` - 正文
  - `tags` - 标签
  - `profile` - 个人资料

#### 微博长图模板
- **尺寸**: 1080px × 任意高度（建议1920px）
- **关键元素**:
  - 吸睛标题
  - 关键数据突出显示
  - 信息图表区域
  - 话题标签
  - 二维码/链接
- **节点命名规范**:
  - `headline` - 主标题
  - `subtitle` - 副标题
  - `key_points` - 关键点
  - `data_viz` - 数据可视化
  - `hashtags` - 话题标签

### 3. 获取文件ID和节点ID

#### 文件ID
1. 打开Figma文件
2. 查看URL: `https://www.figma.com/file/{FILE_ID}/文件名`
3. 复制 `FILE_ID`

#### 节点ID
1. 在Figma中选中元素
2. 右侧面板查看 `ID` 字段
3. 或通过Figma API获取所有节点ID

### 4. 配置映射关系

在 `config/config.yaml` 中添加：

```yaml
figma:
  access_token: "${FIGMA_ACCESS_TOKEN}"  # 从环境变量读取
  templates:
    wechat_article:
      file_key: "你的公众号模板文件ID"
      node_map:
        title: "节点ID_标题"
        author: "节点ID_作者"
        date: "节点ID_日期"
        content: "节点ID_正文"
        cover_image: "节点ID_封面图"
    
    xiaohongshu_note:
      file_key: "你的小红书模板文件ID"
      node_map:
        cover: "节点ID_封面"
        title: "节点ID_标题"
        content: "节点ID_正文"
        tags: "节点ID_标签"
    
    weibo_card:
      file_key: "你的微博模板文件ID"
      node_map:
        headline: "节点ID_主标题"
        subtitle: "节点ID_副标题"
        key_points: "节点ID_关键点"
        hashtags: "节点ID_话题标签"
```

### 5. 自动化工作流程

#### 完整流程：
1. **AI生成内容** → 2. **Figma填充模板** → 3. **导出图片** → 4. **多平台发布**

#### API调用示例：
```python
# 初始化客户端
figma = FigmaClient()

# 创建多平台设计
designs = figma.batch_create_designs({
    'title': 'AI芯片竞争加剧',
    'content': '详细分析内容...',
    'author': 'AI智汇观察',
    'tags': ['科技', 'AI芯片', '投资'],
    'images': ['image_url1', 'image_url2']
})

# 导出图片
for platform, design in designs['designs'].items():
    exports = figma.export_design(
        design['file_key'],
        list(design['node_map'].values()),
        formats=['png', 'jpg']
    )
    
    # 保存到文件
    for format, images in exports.items():
        for node_id, image_url in images.items():
            # 下载图片
            save_image(image_url, f"{platform}_{node_id}.{format}")
```

### 6. 最佳实践

#### 设计建议：
1. **使用组件（Components）**: 创建可复用的设计元素
2. **样式一致**: 统一字体、颜色、间距
3. **响应式考虑**: 确保在不同设备上显示良好
4. **留白充足**: 提高可读性

#### 技术建议：
1. **缓存设计文件**: 减少API调用
2. **批量处理**: 一次导出多个平台的图片
3. **错误处理**: 处理网络超时和API限制
4. **日志记录**: 记录所有操作便于调试

### 7. 故障排除

#### 常见问题：
1. **API权限不足**: 检查token权限
2. **节点ID错误**: 确认节点存在且可访问
3. **导出失败**: 检查网络和文件权限
4. **设计错位**: 验证模板尺寸和布局

#### 调试工具：
```bash
# 测试API连接
python -c "import os; from scripts.design.figma_client import FigmaClient; client = FigmaClient(); print('✅ 连接成功' if client.access_token else '❌ 需要配置token')"

# 获取文件信息
python scripts/design/figma_client.py
```

### 8. 安全注意事项

1. **保护Access Token**:
   - 不要提交到代码仓库
   - 使用环境变量或密钥管理
   - 定期轮换token

2. **文件权限**:
   - 模板文件设置为私有或团队可见
   - 限制编辑权限
   - 定期备份设计文件

3. **API限制**:
   - 遵守Figma API使用条款
   - 注意速率限制（30次/分钟）
   - 监控API使用量

---

## 🚀 快速开始清单

- [ ] 获取Figma Personal Access Token
- [ ] 创建模板设计文件
- [ ] 获取文件ID和节点ID
- [ ] 配置 `config/config.yaml`
- [ ] 设置环境变量 `FIGMA_ACCESS_TOKEN`
- [ ] 测试API连接
- [ ] 集成到自动化流水线

完成以上步骤后，你的AI博客系统将能够自动生成精美排版并发布到多个平台！