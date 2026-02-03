/**
 * JSON修复工具 - 用于处理模型生成的不完整JSON
 */

function fixJSON(jsonString) {
  if (!jsonString || typeof jsonString !== 'string') {
    return jsonString;
  }

  let fixed = jsonString;
  
  // 1. 尝试直接解析
  try {
    JSON.parse(fixed);
    return fixed; // 已经是有效的JSON
  } catch (e) {
    console.log('初始JSON解析失败，开始修复...');
  }

  // 2. 修复常见的JSON问题
  const fixes = [
    // 修复未闭合的字符串
    () => {
      // 查找未闭合的双引号
      let quoteCount = 0;
      let inString = false;
      let escapeNext = false;
      
      for (let i = 0; i < fixed.length; i++) {
        const char = fixed[i];
        
        if (escapeNext) {
          escapeNext = false;
          continue;
        }
        
        if (char === '\\') {
          escapeNext = true;
          continue;
        }
        
        if (char === '"') {
          if (!inString) {
            inString = true;
          } else {
            inString = false;
          }
        }
      }
      
      // 如果在字符串中结束，添加闭合引号
      if (inString) {
        fixed += '"';
      }
    },
    
    // 修复未闭合的对象和数组
    () => {
      let braceCount = 0;
      let bracketCount = 0;
      
      for (let i = 0; i < fixed.length; i++) {
        const char = fixed[i];
        if (char === '{') braceCount++;
        if (char === '}') braceCount--;
        if (char === '[') bracketCount++;
        if (char === ']') bracketCount--;
      }
      
      // 添加缺失的闭合括号
      while (braceCount > 0) {
        fixed += '}';
        braceCount--;
      }
      
      while (bracketCount > 0) {
        fixed += ']';
        bracketCount--;
      }
    },
    
    // 修复转义字符
    () => {
      // 修复未转义的控制字符
      fixed = fixed.replace(/[\x00-\x1F\x7F]/g, (match) => {
        const code = match.charCodeAt(0);
        return `\\u${code.toString(16).padStart(4, '0')}`;
      });
      
      // 修复未转义的双引号
      fixed = fixed.replace(/(?<!\\)"(?=\s*[,\]}])/g, '\\"');
    },
    
    // 修复尾随逗号
    () => {
      fixed = fixed.replace(/,(\s*[\]}])/g, '$1');
    }
  ];

  // 应用所有修复
  for (const fix of fixes) {
    try {
      fix();
    } catch (e) {
      console.log('修复步骤失败:', e.message);
    }
  }

  // 3. 尝试再次解析
  try {
    JSON.parse(fixed);
    console.log('JSON修复成功');
    return fixed;
  } catch (e) {
    console.log('JSON修复失败，尝试提取有效部分:', e.message);
    
    // 4. 如果仍然失败，尝试提取有效的JSON对象
    try {
      // 查找最长的有效JSON前缀
      for (let i = fixed.length - 1; i > 0; i--) {
        try {
          const partial = fixed.substring(0, i);
          JSON.parse(partial);
          console.log(`提取了前${i}个字符的有效JSON`);
          return partial;
        } catch (e) {
          continue;
        }
      }
    } catch (e) {
      console.log('无法提取有效JSON');
    }
    
    // 5. 最后手段：包装为字符串
    return JSON.stringify({ error: 'invalid_json', original: fixed.substring(0, 500) });
  }
}

/**
 * 安全解析JSON，带有自动修复
 */
function safeParseJSON(jsonString, defaultValue = {}) {
  try {
    const fixed = fixJSON(jsonString);
    return JSON.parse(fixed);
  } catch (e) {
    console.error('JSON解析失败:', e.message);
    console.error('原始字符串（前200字符）:', jsonString.substring(0, 200));
    return defaultValue;
  }
}

module.exports = {
  fixJSON,
  safeParseJSON
};