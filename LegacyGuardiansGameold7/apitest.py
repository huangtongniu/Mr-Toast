# test_api_clean.py (已清理版本)
import os
from openai import OpenAI
import getpass

# --- 1. 提示用户输入API密钥 ---
print("=====================================================")
print(" OpenAI API 密钥有效性测试工具")
print("=====================================================")
print("请从您的 OpenAI 账户复制 API 密钥。")
print("在下方光标处粘贴密钥后按 Enter 键。输入内容将不可见，这是为了安全。")

# 使用 getpass 安全地获取密钥，不会在屏幕上显示
try:
    my_api_key = getpass.getpass("请输入您的 OpenAI API 密钥: ")
except Exception as e:
    print(f"\n无法读取输入: {e}")
    my_api_key = None

# --- 2. 运行测试 ---
print("\n正在尝试连接到 OpenAI API...")

if not my_api_key:
    print("\n错误：没有检测到 API 密钥输入。")
else:
    try:
        # 初始化 OpenAI 客户端
        client = OpenAI(api_key=my_api_key)

        # 准备一个清晰的、用于测试的 Prompt
        system_prompt = "You are a helpful assistant."
        user_prompt = "Hello! Please confirm the test is working by saying 'Test successful'."
        
        print(f"\n正在向模型 '{'gpt-4o-mini'}' 发送以下 Prompt:")
        print(f"  System: {system_prompt}")
        print(f"  User: {user_prompt}")

        # 发送测试请求
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=20,
            temperature=0.1
        )

        # 打印返回的结果
        response_message = completion.choices[0].message.content
        
        print("\n-------------------------------------------")
        print("✅ API 密钥有效，测试成功！")
        print(f"🤖 OpenAI 返回的消息: '{response_message.strip()}'")
        print("-------------------------------------------")

    except Exception as e:
        # 如果发生任何错误，打印错误信息
        print("\n-------------------------------------------")
        print("❌ API 测试失败。")
        print("错误详情:")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {e}")
        print("\n可能的原因：")
        print("  1. 您输入的API密钥不正确或已失效。")
        print("  2. 您的OpenAI账户额度已用尽。")
        print("  3. 您的网络无法连接到OpenAI服务器。")
        print("-------------------------------------------")