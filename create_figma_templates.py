#!/usr/bin/env python3
"""
通过Figma API自动创建设计模板
注意：Figma REST API创建文件功能有限，这里提供创建指南
"""

import os
import json
import requests
from typing import Dict, List, Optional

def check_figma_access():
    """检查Figma访问权限"""
    token = os.getenv('FIGMA_ACCESS_TOKEN')
    if not token:
        print("❌ 未设置 FIGMA_ACCESS_TOKEN 环境变量")
        print("   运行: export FIGMA_ACCESS_TOKEN=你的token")
        return None
    
    headers = {'X-Figma-Token': token}
    
    # 检查token有效性
    try:
        response = requests.get('https://api.figma.com/v1/me', headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Figma账户: {user_data.get('email')} ({user_data.get('handle')})")
            return token
        else:
            print(f"❌ Token无效: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None

def get_existing_file(file_id: str, token: str) -> Optional[Dict]:
    """获取现有文件信息"""
    headers = {'X-Figma-Token': token}
    
    try:
        response = requests.get(f'https://api.figma.com/v1/files/{file_id}', headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 获取文件失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def create_template_structure():
    """创建模板结构指南"""
    print("\n🎨 手动创建模板步骤:")
    print("=" * 60)
    
    print("""
1. 打开Figma文件: AI-Blog-Templates (ID: GHZFIC9s6XJsNWKlA6XOl3)

2. 设计公众号模板页面:
   - 页面名称: "公众号模板"
   - 画板尺寸: 900px × 动态高度
   - 关键元素:
     * 标题框 (命名: title)
     * 副标题/日期 (命名: subtitle)
     * 正文区域 (命名: content)
     * 数据卡片 (命名: data_card_1, data_card_2)
     * 关键点列表 (命名: key_points)
     * 建议区域 (命名: recommendations)
     * 二维码/关注区域 (命名: qrcode)

3. 设计小红书模板页面:
   - 页面名称: "小红书模板"
   - 画板尺寸: 1242px × 1660px
   - 关键元素:
     * 封面图区域 (命名: cover)
     * 标题 (命名: title)
     * 关键数据 (命名: key_data)
     * 核心要点 (命名: core_points)
     * 投资建议 (命名: recommendations)
     * 标签区域 (命名: tags)
     * 个人资料 (命名: profile)

4. 设计微博模板页面:
   - 页面名称: "微博模板"
   - 画板尺寸: 1080px × 1920px
   - 关键元素:
     * 主标题 (命名: headline)
     * 日期 (命名: date)
     * 趋势卡片 (命名: trend_1, trend_2, trend_3)
     * 关键数据 (命名: key_stats)
     * 核心观点 (命名: core_viewpoints)
     * 明日关注 (命名: tomorrow_focus)
     * 话题标签 (命名: hashtags)
     * 二维码 (命名: qrcode)

5. 应用设计规范:
   - 主色: #2962ff (科技蓝)
   - 辅色: #1a237e (深蓝), #ff6d00 (亮橙)
   - 字体: 思源黑体
   - 间距: 8px/16px/32px系统
""")

def generate_node_mapping_guide():
    """生成节点映射配置指南"""
    print("\n🔧 节点映射配置:")
    print("=" * 60)
    
    config_template = {
        'figma': {
            'access_token': '${FIGMA_ACCESS_TOKEN}',
            'enabled': True,
            'templates': {
                'wechat_article': {
                    'file_key': 'GHZFIC9s6XJsNWKlA6XOl3',
                    'node_map': {
                        'title': 'REPLACE_WITH_TITLE_NODE_ID',
                        'subtitle': 'REPLACE_WITH_SUBTITLE_NODE_ID',
                        'content': 'REPLACE_WITH_CONTENT_NODE_ID',
                        'key_points': 'REPLACE_WITH_KEY_POINTS_NODE_ID',
                        'recommendations': 'REPLACE_WITH_RECOMMENDATIONS_NODE_ID',
                        'qrcode': 'REPLACE_WITH_QRCODE_NODE_ID'
                    }
                },
                'xiaohongshu_note': {
                    'file_key': 'GHZFIC9s6XJsNWKlA6XOl3',
                    'node_map': {
                        'cover': 'REPLACE_WITH_COVER_NODE_ID',
                        'title': 'REPLACE_WITH_TITLE_NODE_ID',
                        'key_data': 'REPLACE_WITH_KEY_DATA_NODE_ID',
                        'core_points': 'REPLACE_WITH_CORE_POINTS_NODE_ID',
                        'recommendations': 'REPLACE_WITH_RECOMMENDATIONS_NODE_ID',
                        'tags': 'REPLACE_WITH_TAGS_NODE_ID',
                        'profile': 'REPLACE_WITH_PROFILE_NODE_ID'
                    }
                },
                'weibo_card': {
                    'file_key': 'GHZFIC9s6XJsNWKlA6XOl3',
                    'node_map': {
                        'headline': 'REPLACE_WITH_HEADLINE_NODE_ID',
                        'date': 'REPLACE_WITH_DATE_NODE_ID',
                        'trend_1': 'REPLACE_WITH_TREND_1_NODE_ID',
                        'trend_2': 'REPLACE_WITH_TREND_2_NODE_ID',
                        'trend_3': 'REPLACE_WITH_TREND_3_NODE_ID',
                        'key_stats': 'REPLACE_WITH_KEY_STATS_NODE_ID',
                        'core_viewpoints': 'REPLACE_WITH_CORE_VIEWPOINTS_NODE_ID',
                        'tomorrow_focus': 'REPLACE_WITH_TOMORROW_FOCUS_NODE_ID',
                        'hashtags': 'REPLACE_WITH_HASHTAGS_NODE_ID',
                        'qrcode': 'REPLACE_WITH_QRCODE_NODE_ID'
                    }
                }
            }
        }
    }
    
    print("复制以下配置到 config/config.yaml:")
    print(json.dumps(config_template, indent=2, ensure_ascii=False))

def get_node_ids_from_file(file_id: str, token: str):
    """从文件获取节点ID"""
    print(f"\n📋 获取文件 {file_id} 的节点结构...")
    
    headers = {'X-Figma-Token': token}
    try:
        response = requests.get(f'https://api.figma.com/v1/files/{file_id}', headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            print("✅ 文件结构获取成功")
            print(f"文件名: {data.get('name')}")
            
            # 提取页面信息
            if 'document' in data and 'children' in data['document']:
                pages = data['document']['children']
                print(f"\n📄 找到 {len(pages)} 个页面:")
                
                for page in pages:
                    if 'name' in page and 'id' in page:
                        print(f"\n  📍 页面: {page['name']} (ID: {page['id']})")
                        
                        # 提取页面内的元素
                        if 'children' in page:
                            elements = page['children']
                            print(f"    包含 {len(elements)} 个元素:")
                            
                            for elem in elements[:10]:  # 只显示前10个元素
                                if 'name' in elem and 'id' in elem:
                                    print(f"      • {elem['name']}: {elem['id']}")
            
            # 保存完整结构到文件
            output_file = f"figma_structure_{file_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 完整结构已保存到: {output_file}")
            
        else:
            print(f"❌ 获取文件失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主函数"""
    print("🎨 Figma模板创建助手")
    print("=" * 60)
    
    # 检查访问权限
    token = check_figma_access()
    if not token:
        return
    
    file_id = "GHZFIC9s6XJsNWKlA6XOl3"
    
    # 获取现有文件信息
    file_info = get_existing_file(file_id, token)
    if file_info:
        print(f"\n📁 现有文件: {file_info.get('name')}")
        print(f"   最后修改: {file_info.get('lastModified')}")
        print(f"   角色: {file_info.get('role')}")
        
        # 显示创建指南
        create_template_structure()
        
        # 获取节点结构
        get_node_ids_from_file(file_id, token)
        
        # 生成配置指南
        generate_node_mapping_guide()
        
        print("\n🚀 下一步:")
        print("1. 按照指南在Figma中设计模板")
        print("2. 获取节点ID（选中元素查看右侧面板）")
        print("3. 更新 config/config.yaml 中的节点映射")
        print("4. 测试自动化发布")
        
    else:
        print(f"\n❌ 无法访问文件 {file_id}")
        print("   请检查文件是否存在或你有访问权限")

if __name__ == "__main__":
    main()