#!/usr/bin/env python3
"""
获取Figma文件节点ID的简单脚本
"""

import os
import sys
import json

def get_file_structure(file_id):
    """获取文件结构"""
    token = os.getenv('FIGMA_ACCESS_TOKEN')
    if not token:
        print("❌ 请设置 FIGMA_ACCESS_TOKEN 环境变量")
        print("   运行: export FIGMA_ACCESS_TOKEN=你的token")
        return None
    
    import requests
    
    url = f"https://api.figma.com/v1/files/{file_id}"
    headers = {'X-Figma-Token': token}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 获取文件失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def extract_nodes(data, indent=0):
    """递归提取节点信息"""
    nodes = []
    
    if isinstance(data, dict):
        # 提取节点信息
        node_info = {
            'id': data.get('id'),
            'name': data.get('name'),
            'type': data.get('type'),
            'visible': data.get('visible', True)
        }
        
        # 只显示可见且有名称的节点
        if node_info['visible'] and node_info['name']:
            nodes.append(node_info)
            prefix = "  " * indent
            print(f"{prefix}📌 {node_info['name']} (ID: {node_info['id']}, 类型: {node_info['type']})")
        
        # 递归处理子节点
        if 'children' in data:
            for child in data['children']:
                nodes.extend(extract_nodes(child, indent + 1))
    
    elif isinstance(data, list):
        for item in data:
            nodes.extend(extract_nodes(item, indent))
    
    return nodes

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python get_figma_nodes.py <文件ID>")
        print("示例: python get_figma_nodes.py GHZFIC9s6XJsNWKlA6XOl3")
        print("\n先设置环境变量:")
        print("  export FIGMA_ACCESS_TOKEN=figd_VV2b7lrIFNS0KCPtds23Sdjpp3jxRj_IMaiYCvd_")
        return
    
    file_id = sys.argv[1]
    
    print(f"🔍 获取Figma文件节点: {file_id}")
    print("=" * 60)
    
    # 获取文件结构
    data = get_file_structure(file_id)
    if not data:
        return
    
    # 提取并显示节点
    print("\n📁 文件结构:")
    print("-" * 30)
    
    if 'document' in data:
        nodes = extract_nodes(data['document'])
        
        print(f"\n✅ 找到 {len(nodes)} 个节点")
        
        # 按类型分组显示
        print("\n📊 节点类型统计:")
        type_count = {}
        for node in nodes:
            node_type = node['type']
            type_count[node_type] = type_count.get(node_type, 0) + 1
        
        for node_type, count in type_count.items():
            print(f"  {node_type}: {count} 个")
        
        # 保存节点列表到文件
        output_file = f"figma_nodes_{file_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(nodes, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 节点列表已保存到: {output_file}")
        
        # 使用指南
        print("\n🎯 如何使用:")
        print("1. 在Figma中查看对应元素")
        print("2. 找到需要的节点ID")
        print("3. 更新 config/config.yaml 中的 node_map")
        print("\n示例配置:")
        print("""
  templates:
    wechat_article:
      file_key: "GHZFIC9s6XJsNWKlA6XOl3"
      node_map:
        title: "10:20"      # 替换为实际节点ID
        content: "30:40"    # 替换为实际节点ID
        author: "50:60"     # 替换为实际节点ID
""")
    else:
        print("❌ 文件结构中没有找到 document 数据")

if __name__ == "__main__":
    # 设置环境变量（测试用）
    if len(sys.argv) > 2 and sys.argv[2] == "--test":
        os.environ['FIGMA_ACCESS_TOKEN'] = 'figd_VV2b7lrIFNS0KCPtds23Sdjpp3jxRj_IMaiYCvd_'
    
    main()