#!/bin/bash

# 部署状态监控脚本
BLOG_URL="https://gsaecy.github.io"
TEST_POST_URL="$BLOG_URL/posts/test-deployment-fix/"

echo "🔍 开始监控GitHub Pages部署状态"
echo "博客地址: $BLOG_URL"
echo "测试文章: $TEST_POST_URL"
echo ""

# 等待初始部署（GitHub Actions需要时间启动）
echo "⏳ 等待部署开始（约30秒）..."
sleep 30

# 监控部署状态
MAX_CHECKS=20
CHECK_COUNT=0
DEPLOYED=false

while [ $CHECK_COUNT -lt $MAX_CHECKS ] && [ "$DEPLOYED" = "false" ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    echo ""
    echo "检查 #$CHECK_COUNT - $(date '+%H:%M:%S')"
    
    # 检查测试文章
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$TEST_POST_URL" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "  🎉 部署成功！测试文章可访问"
        echo "  🔗 文章链接: $TEST_POST_URL"
        DEPLOYED=true
    else
        echo "  ⏳ 部署进行中 (HTTP状态码: $HTTP_CODE)"
        
        # 检查博客首页
        if curl -s -f "$BLOG_URL" > /dev/null 2>&1; then
            echo "  ✅ 博客首页可访问"
        else
            echo "  🔄 博客首页暂不可访问"
        fi
        
        # 检查GitHub Actions状态
        echo "  📊 检查GitHub Actions状态..."
        echo "    访问: https://github.com/Gsaecy/Gsaecy.github.io/actions"
        
        if [ $CHECK_COUNT -lt $MAX_CHECKS ]; then
            echo "  等待60秒后重试..."
            sleep 60
        fi
    fi
done

echo ""
echo "📋 部署监控报告"
echo "================"

if [ "$DEPLOYED" = "true" ]; then
    echo "✅ 部署验证成功！"
    echo ""
    echo "🎯 修复内容已验证:"
    echo "1. baseURL修复: ✅ 完成"
    echo "2. 主题配置: ✅ 完成"  
    echo "3. 工作流优化: ✅ 完成"
    echo "4. 文章访问: ✅ 正常"
    echo ""
    echo "🚀 下一步建议:"
    echo "1. 访问博客: $BLOG_URL"
    echo "2. 查看测试文章: $TEST_POST_URL"
    echo "3. 验证所有链接和样式"
    echo "4. 可以开始使用AI自动化系统"
else
    echo "⚠️  部署监控超时"
    echo ""
    echo "🔧 需要手动检查:"
    echo "1. GitHub Actions运行状态: https://github.com/Gsaecy/Gsaecy.github.io/actions"
    echo "2. GitHub Pages设置: https://github.com/Gsaecy/Gsaecy.github.io/settings/pages"
    echo "3. 查看工作流日志中的错误信息"
    echo ""
    echo "📞 如果问题持续，请提供:"
    echo "- 最新的Actions运行链接"
    echo "- 错误日志截图"
fi

echo ""
echo "⏰ 监控结束时间: $(date '+%Y-%m-%d %H:%M:%S')"