#!/usr/bin/env node

/**
 * 测试脚本：诊断JSON解析问题
 */

const fs = require('fs');
const path = require('path');

// 模拟可能出问题的JSON字符串
const problematicJSONs = [
  // 1. 未闭合的字符串
  '{"message": "这是一个未闭合的字符串}',
  
  // 2. 包含换行符的字符串
  '{"message": "第一行\n第二行\n第三行"}',
  
  // 3. 包含未转义引号的字符串
  '{"message": "他说："你好世界""}',
  
  // 4. 包含控制字符的字符串
  '{"message": "包含\t制表符和\r回车符"}',
  
  // 5. 未闭合的对象
  '{"data": {"nested": {"value": "test"}}',
  
  // 6. 尾随逗号
  '{"a": 1, "b": 2,}',
  
  // 7. 位置15196附近的模拟问题（长字符串）
  `{"long_string": "${'x'.repeat(15190)}未闭合"}`,
  
  // 8. Unicode字符
  '{"message": "中文测试 🚀 emoji和特殊字符"}'
];

console.log('测试各种JSON解析问题...\n');

problematicJSONs.forEach((jsonStr, index) => {
  console.log(`测试 ${index + 1}:`);
  console.log(`类型: ${describeIssue(jsonStr)}`);
  console.log(`长度: ${jsonStr.length} 字符`);
  
  try {
    JSON.parse(jsonStr);
    console.log('✅ 解析成功\n');
  } catch (error) {
    console.log(`❌ 解析失败: ${error.message}`);
    console.log(`位置: ${getErrorPosition(error, jsonStr)}`);
    console.log('修复建议:', getFixSuggestion(error, jsonStr));
    console.log('');
  }
});

// 测试修复函数
console.log('\n=== 测试修复函数 ===\n');
const { fixJSON } = require('./json_fixer.js');

problematicJSONs.forEach((jsonStr, index) => {
  console.log(`修复测试 ${index + 1}:`);
  const fixed = fixJSON(jsonStr);
  
  try {
    JSON.parse(fixed);
    console.log('✅ 修复后解析成功');
  } catch (error) {
    console.log(`❌ 修复后仍然失败: ${error.message}`);
  }
  
  console.log(`原始长度: ${jsonStr.length}, 修复后长度: ${fixed.length}`);
  console.log('');
});

function describeIssue(jsonStr) {
  if (jsonStr.includes('\n')) return '包含换行符';
  if (jsonStr.includes('\t') || jsonStr.includes('\r')) return '包含控制字符';
  if (jsonStr.match(/[^\x20-\x7E]/)) return '包含非ASCII字符';
  if (jsonStr.includes(',}') || jsonStr.includes(',]')) return '尾随逗号';
  if ((jsonStr.match(/"/g) || []).length % 2 !== 0) return '未闭合的引号';
  if ((jsonStr.match(/{/g) || []).length > (jsonStr.match(/}/g) || []).length) return '未闭合的对象';
  if ((jsonStr.match(/\[/g) || []).length > (jsonStr.match(/\]/g) || []).length) return '未闭合的数组';
  return '未知问题';
}

function getErrorPosition(error, jsonStr) {
  const match = error.message.match(/position (\d+)/);
  if (match) {
    const pos = parseInt(match[1]);
    const start = Math.max(0, pos - 20);
    const end = Math.min(jsonStr.length, pos + 20);
    return `位置 ${pos}: "...${jsonStr.substring(start, end)}..."`;
  }
  return '未知位置';
}

function getFixSuggestion(error, jsonStr) {
  const errorMsg = error.message.toLowerCase();
  
  if (errorMsg.includes('unterminated string')) {
    return '添加缺失的闭合引号或转义字符串中的引号';
  }
  
  if (errorMsg.includes('unexpected token')) {
    return '检查特殊字符和转义序列';
  }
  
  if (errorMsg.includes('end of json')) {
    return 'JSON可能被截断，检查响应完整性';
  }
  
  return '使用json_fixer.js中的修复函数';
}

console.log('\n=== 建议的解决方案 ===');
console.log('1. 在飞书插件中集成json_fixer.js');
console.log('2. 调整模型参数（已配置：temperature=0.2）');
console.log('3. 检查网络传输中的字符编码');
console.log('4. 考虑使用更稳定的模型（如GPT-5.2）作为备选');