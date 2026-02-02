#!/usr/bin/env python3
"""
微信公众号自动发布器
将AI生成的文章自动发布到微信公众号
"""

import os
import json
import time
import logging
from typing import Dict, Optional, List
import requests
from datetime import datetime

from scripts.utils.logger import setup_logger
from scripts.utils.config_loader import load_config

logger = setup_logger("wechat_publisher")


class WeChatPublisher:
    """微信公众号发布器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化发布器"""
        self.config = load_config(config_path)
        self.wechat_config = self.config.get('wechat', {})
        
        # 微信公众号API配置
        self.app_id = os.getenv('WECHAT_APP_ID', self.wechat_config.get('app_id', ''))
        self.app_secret = os.getenv('WECHAT_APP_SECRET', self.wechat_config.get('app_secret', ''))
        self.access_token = None
        self.token_expire_time = 0
        
        # 发布配置
        self.auto_publish = self.wechat_config.get('auto_publish', False)
        self.draft_mode = self.wechat_config.get('draft_mode', True)  # 默认为草稿
        self.cover_image = self.wechat_config.get('cover_image', '')
        
        logger.info(f"微信公众号发布器初始化完成，自动发布: {self.auto_publish}")
    
    def get_access_token(self) -> Optional[str]:
        """获取微信公众号access_token"""
        # 检查token是否过期（提前5分钟刷新）
        if self.access_token and time.time() < self.token_expire_time - 300:
            return self.access_token
        
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                self.token_expire_time = time.time() + data.get('expires_in', 7200)
                logger.info("微信公众号access_token获取成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            return None
    
    def optimize_for_wechat(self, article_content: str, metadata: Dict) -> Dict:
        """优化文章内容为微信公众号格式"""
        # 提取文章基本信息
        title = metadata.get('title', '行业分析报告')
        description = metadata.get('description', '每日AI驱动的行业深度分析')
        tags = metadata.get('tags', ['行业分析', 'AI'])
        
        # 公众号标题优化
        wechat_title = self._optimize_title(title)
        
        # 公众号摘要优化
        wechat_summary = self._optimize_summary(description, article_content)
        
        # 正文优化
        wechat_content = self._optimize_content(article_content)
        
        # 封面图处理
        cover_image = self._get_cover_image(metadata)
        
        return {
            'title': wechat_title,
            'author': 'AI智汇观察',
            'digest': wechat_summary,
            'content': wechat_content,
            'content_source_url': metadata.get('url', 'https://gsaecy.github.io'),
            'thumb_media_id': cover_image,
            'show_cover_pic': 1,
            'need_open_comment': 1,
            'only_fans_can_comment': 0,
            'tags': tags
        }
    
    def _optimize_title(self, title: str) -> str:
        """优化标题（公众号标题要求吸引人）"""
        # 添加emoji和优化格式
        title_mapping = {
            'AI芯片': '🚀 AI芯片',
            '云计算': '☁️ 云计算', 
            '自动驾驶': '🤖 自动驾驶',
            '金融科技': '💰 金融科技',
            '行业分析': '📊 行业分析'
        }
        
        optimized = title
        for key, value in title_mapping.items():
            if key in optimized:
                optimized = optimized.replace(key, value)
        
        # 确保标题长度合适（公众号建议不超过64字符）
        if len(optimized) > 64:
            optimized = optimized[:61] + '...'
        
        return optimized
    
    def _optimize_summary(self, description: str, content: str) -> str:
        """优化摘要（公众号摘要栏显示）"""
        if description and len(description) <= 120:
            return description
        
        # 从内容中提取关键句作为摘要
        sentences = content.split('。')
        key_sentences = []
        
        keywords = ['关键', '重要', '突破', '增长', '下降', '趋势', '机会', '风险']
        for sentence in sentences:
            if any(keyword in sentence for keyword in keywords) and len(sentence) > 10:
                key_sentences.append(sentence.strip())
                if len(key_sentences) >= 2:
                    break
        
        summary = '。'.join(key_sentences)
        if len(summary) > 120:
            summary = summary[:117] + '...'
        
        return summary if summary else "每日AI驱动的行业深度分析报告"
    
    def _optimize_content(self, content: str) -> str:
        """优化正文内容（公众号富文本格式）"""
        # 添加公众号特定的格式优化
        optimized = content
        
        # 1. 添加开头引导语
        guide = '''<p style="text-align: center;"><strong>👋 大家好，我是AI智汇观察</strong></p>
<p style="text-align: center;">每日为你带来最新的行业深度分析</p>
<hr>'''
        optimized = guide + '\n\n' + optimized
        
        # 2. 关键数据加粗
        import re
        # 匹配百分比数据
        optimized = re.sub(r'(\d+%)', r'<strong>\1</strong>', optimized)
        # 匹配金额数据
        optimized = re.sub(r'(\$\d+[BM]?)', r'<strong>\1</strong>', optimized)
        
        # 3. 添加小标题样式
        optimized = re.sub(r'## (.*?)', r'<h2 style="color: #1890ff;">\1</h2>', optimized)
        optimized = re.sub(r'### (.*?)', r'<h3 style="color: #52c41a;">\1</h3>', optimized)
        
        # 4. 添加结尾引导关注
        footer = f'''<hr>
<p style="text-align: center;">📅 报告时间：{datetime.now().strftime("%Y年%m月%d日")}</p>
<p style="text-align: center;">🤖 本报告由AI智汇观察系统自动生成</p>
<p style="text-align: center;">🔍 关注公众号，每日获取最新行业分析</p>'''
        optimized = optimized + '\n\n' + footer
        
        return optimized
    
    def _get_cover_image(self, metadata: Dict) -> str:
        """获取封面图media_id"""
        # 这里需要先上传图片到微信公众号获取media_id
        # 简化实现：返回配置的默认封面图或占位符
        if self.cover_image:
            return self.cover_image
        
        # 根据文章类型选择默认封面
        tags = metadata.get('tags', [])
        if '科技' in tags or 'AI' in tags:
            return 'tech_cover'
        elif '金融' in tags:
            return 'finance_cover'
        elif '教育' in tags:
            return 'education_cover'
        else:
            return 'default_cover'
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """上传图片到微信公众号"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"https://api.weixin.qq.com/cgi-bin/media/upload"
        params = {'access_token': access_token, 'type': 'image'}
        
        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, params=params, files=files, timeout=30)
                data = response.json()
                
                if 'media_id' in data:
                    logger.info(f"图片上传成功: {image_path}")
                    return data['media_id']
                else:
                    logger.error(f"图片上传失败: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"图片上传异常: {e}")
            return None
    
    def create_draft(self, article_data: Dict) -> Optional[str]:
        """创建草稿"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add"
        params = {'access_token': access_token}
        
        # 构建文章数据
        articles = [{
            'title': article_data['title'],
            'author': article_data['author'],
            'digest': article_data['digest'],
            'content': article_data['content'],
            'content_source_url': article_data['content_source_url'],
            'thumb_media_id': article_data['thumb_media_id'],
            'show_cover_pic': article_data['show_cover_pic'],
            'need_open_comment': article_data['need_open_comment'],
            'only_fans_can_comment': article_data['only_fans_can_comment']
        }]
        
        payload = {
            'articles': articles
        }
        
        try:
            response = requests.post(url, params=params, json=payload, timeout=30)
            data = response.json()
            
            if 'media_id' in data:
                logger.info(f"草稿创建成功: {article_data['title']}")
                return data['media_id']
            else:
                logger.error(f"草稿创建失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"草稿创建异常: {e}")
            return None
    
    def publish_article(self, media_id: str) -> bool:
        """发布文章"""
        if not self.auto_publish:
            logger.info("自动发布未启用，文章保存为草稿")
            return True
        
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit"
        params = {'access_token': access_token}
        
        payload = {
            'media_id': media_id
        }
        
        try:
            response = requests.post(url, params=params, json=payload, timeout=30)
            data = response.json()
            
            if data.get('errcode') == 0:
                logger.info(f"文章发布成功: {media_id}")
                return True
            else:
                logger.error(f"文章发布失败: {data}")
                return False
                
        except Exception as e:
            logger.error(f"文章发布异常: {e}")
            return False
    
    def publish_to_wechat(self, article_path: str, metadata: Dict) -> Dict:
        """发布文章到微信公众号"""
        result = {
            'success': False,
            'message': '',
            'media_id': None,
            'published': False
        }
        
        try:
            # 读取文章内容
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 优化为公众号格式
            wechat_data = self.optimize_for_wechat(content, metadata)
            
            # 创建草稿
            media_id = self.create_draft(wechat_data)
            if not media_id:
                result['message'] = '创建草稿失败'
                return result
            
            result['media_id'] = media_id
            
            # 发布文章（如果启用自动发布）
            if self.auto_publish:
                published = self.publish_article(media_id)
                result['published'] = published
                result['message'] = '发布成功' if published else '发布失败'
            else:
                result['message'] = '已保存为草稿'
            
            result['success'] = True
            logger.info(f"微信公众号处理完成: {article_path}")
            
        except Exception as e:
            result['message'] = f'处理异常: {str(e)}'
            logger.error(f"微信公众号发布异常: {e}")
        
        return result


def main():
    """测试函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python wechat_publisher.py <文章路径>")
        return
    
    article_path = sys.argv[1]
    
    # 模拟文章元数据
    metadata = {
        'title': '科技行业日报：AI芯片竞争加剧与云计算价格战',
        'description': '今日科技行业三大趋势分析',
        'tags': ['科技', 'AI芯片', '云计算'],
        'url': 'https://gsaecy.github.io'
    }
    
    publisher = WeChatPublisher()
    result = publisher.publish_to_wechat(article_path, metadata)
    
    print(f"发布结果: {result}")


if __name__ == "__main__":
    main()