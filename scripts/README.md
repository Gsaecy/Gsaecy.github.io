# 自动化脚本目录

这是AI行业观察站的自动化脚本目录，包含信息采集、分析和发布的完整流程。

## 📁 目录结构

```
scripts/
├── collectors/     # 信息采集脚本
│   ├── tech_news.py    # 科技新闻采集
│   ├── finance_data.py # 金融数据采集
│   └── social_trends.py # 社交趋势采集
├── analyzers/      # AI分析脚本
│   ├── summarizer.py   # 信息总结
│   ├── analyzer.py     # 深度分析
│   └── generator.py    # 文章生成
├── publishers/     # 发布脚本
│   ├── hugo_post.py    # Hugo文章生成
│   └── deploy.py       # 部署脚本
└── main.py        # 主控制脚本
```

## 🚀 工作流程

1. **信息采集** (`collectors/`)
   - 定时从各渠道采集行业信息
   - 数据清洗和格式化
   - 存储到 `data/` 目录

2. **AI分析** (`analyzers/`)
   - 调用GPT API进行信息分析
   - 生成结构化分析报告
   - 趋势判断和机会识别

3. **内容生成** (`generators/`)
   - 根据分析结果生成Markdown文章
   - 添加元数据（标签、分类等）
   - 格式化输出

4. **自动发布** (`publishers/`)
   - 将文章写入Hugo content目录
   - 触发GitHub Actions部署
   - 发送通知

## ⚙️ 配置说明

配置文件位于 `config/config.yaml`：

```yaml
openai:
  api_key: "your-api-key"
  model: "gpt-4"
  
sources:
  tech:
    - "https://36kr.com"
    - "https://huxiu.com"
  finance:
    - "https://wallstreetcn.com"
  
schedule:
  daily: "0 10 * * *"  # 每天10点
```

## 🔧 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置API密钥：
```bash
cp config/config.example.yaml config/config.yaml
# 编辑config.yaml，添加你的OpenAI API密钥
```

3. 测试运行：
```bash
python scripts/main.py --test
```

4. 设置定时任务：
```bash
# 使用crontab或GitHub Actions
```

## 📊 数据存储

采集的数据存储在 `data/` 目录：
- `data/raw/`：原始采集数据
- `data/processed/`：处理后的数据
- `data/articles/`：生成的Markdown文章

## 🐛 故障排除

常见问题：
1. API密钥错误：检查config.yaml配置
2. 网络连接问题：检查代理设置
3. 存储空间不足：清理旧数据
4. 部署失败：检查GitHub Actions日志

## 📈 监控和日志

- 日志文件：`logs/` 目录
- 运行状态：`status.json`
- 错误报告：自动发送到指定邮箱

## 🔄 更新和维护

定期更新：
1. 更新依赖包
2. 优化采集规则
3. 调整分析模型
4. 修复已知问题