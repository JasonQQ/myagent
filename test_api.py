#!/usr/bin/env python3
"""
测试OpenAI API连接
"""

import openai
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

def test_openai_api():
    """测试OpenAI API连接"""
    
    # 获取环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: 未设置")
    print(f"Base URL: {base_url}")
    print()
    
    # 设置OpenAI客户端
    openai.api_key = api_key
    if base_url:
        openai.base_url = base_url
    
    try:
        # 测试API调用
        print("正在测试API连接...")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "你好，请简单回复'测试成功'"}
            ],
            max_tokens=50
        )
        
        print(f"响应类型: {type(response)}")
        print(f"响应内容: {response}")
        
        if hasattr(response, 'choices'):
            content = response.choices[0].message.content
            print(f"API响应: {content}")
            print("✅ API连接成功！")
        else:
            print("⚠️ API返回了非标准格式的响应")
            print(f"响应内容: {response}")
        
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    test_openai_api() 