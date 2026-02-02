#!/usr/bin/env python3
"""
安全更新Figma配置 - 不包含敏感token
"""

import os
import yaml
import json

def update_config_with_file_id(file_id):
    """使用文件ID更新配置"""
    
    # 读取现有配置
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 确保figma配置存在
        if 'figma' not in config:
            config['figma'] = {}
        
        # 更新配置（不包含token）
        config['figma'].update({
            'access_token': '${FIGMA_ACCESS_TOKEN}',  # 从环境变量读取
            'enabled': True,
            'templates': {
                'wechat_article': {
                    'file_key': file_id,
                    'node_map': {
                        'title': 'YOUR_TITLE_NODE_ID',
                        'content': 'YOUR_CONTENT_NODE_ID',
                        'author': 'YOUR_AUTHOR_NODE_ID',
                        'date': 'YOUR_DATE_NODE_ID',
                        'cover_image': 'YOUR_COVER_NODE_ID'
                    }
                },
                'xiaohongshu_note': {
                    'file_key': file_id,
                    'node_map': {
                        'cover': 'YOUR_COVER_NODE_ID',
                        'title': 'YOUR_TITLE_NODE_ID',
                        'content': 'YOUR_CONTENT_NODE_ID',
                        'tags': 'YOUR_TAGS_NODE_ID'
                    }
                },
                'weibo_card': {
                    'file_key': file_id,
                    'node_map': {
                        'headline': 'YOUR_HEADLINE_NODE_ID',
                        'subtitle': 'YOUR_SUBTITLE_NODE_ID',
                        'key_points': 'YOUR_KEYPOINTS_NODE_ID',
                        'hashtags': 'YOUR_HASHTAGS_NODE_ID'
                    }
                }
            }
        })
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✅ 配置文件已更新")
        print(f"   文件ID: {file_id}")
        print(f"   配置文件: {config_path}")
        
        # 显示下一步指南
        print("\n📋 下一步:")
        print("1. 在Figma中获取节点ID:")
        print("   - 选中元素，查看右侧面板的ID")
        print("   - 或运行: python scripts/design/figma_client.py --get-nodes {file_id}")
        print("\n2. 更新节点ID映射:")
        print("   - 编辑 config/config.yaml")
        print("   - 将 YOUR_*_NODE_ID 替换为实际ID")
        print("\n3. 配置GitHub Secrets:")
        print("   - FIGMA_ACCESS_TOKEN = 你的token")
        print("\n4. 测试连接:")
        print("   - export FIGMA_ACCESS_TOKEN=你的token")
        print("   - python test_figma_api.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新配置失败: {e}")
        return False

def get_node_ids_guide(file_id):
    """获取节点ID的详细指南"""
    print(f"\n🔧 如何获取节点ID (文件: {file_id}):")
    print("=" * 60)
    
    print("""
方法1: 使用API获取所有节点
运行以下命令获取文件结构:
```bash
export FIGMA_ACCESS_TOKEN=你的token
curl -s -H "X-Figma-Token: $FIGMA_ACCESS_TOKEN" \\
  "https://api.figma.com/v1/files/{file_id}" | \\
  python3 -c "import sys,json; data=json.load(sys.stdin); 
  print(json.dumps(data['document'], indent=2))"
```

方法2: 使用我们的辅助脚本
```bash
# 安装依赖
pip install requests

# 运行节点获取工具
python scripts/design/figma_client.py --file {file_id} --get-nodes
```

方法3: 手动在Figma中查看
1. 在Figma中打开文件
2. 选中设计元素
3. 右侧面板查看属性
4. 查找"ID"字段

方法4: 使用Figma插件
1. 安装Figma插件: "Copy as JSON" 或 "Design Lint"
2. 导出文件结构为JSON
3. 查找节点ID
""".format(file_id=file_id))

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python update_figma_config.py <文件ID>")
        print("示例: python update_figma_config.py GHZFIC9s6XJsNWKlA6XOl3")
        return
    
    file_id = sys.argv[1]
    
    print("🔄 更新Figma配置")
    print("=" * 60)
    
    # 更新配置
    if update_config_with_file_id(file_id):
        # 显示节点ID获取指南
        get_node_ids_guide(file_id)
        
        print("\n🎯 完成配置后，系统将能够:")
        print("1. 自动从Figma读取模板")
        print("2. 填充AI生成的内容")
        print("3. 导出精美设计图片")
        print("4. 发布到多平台")
    else:
        print("\n🔧 需要手动配置:")
        print("1. 编辑 config/config.yaml")
        print("2. 添加figma配置部分")
        print("3. 设置文件ID和节点映射")

if __name__ == "__main__":
    main()