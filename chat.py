from openai import OpenAI
import os
import json
import time

# DeepSeek API 配置
DEEPSEEK_API_KEY = (
    ""  # 请在这里填入你的 DeepSeek API Key
)
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 全局 OpenAI 客户端
_client = None

def _get_deepseek_client():
    """获取 DeepSeek 客户端实例"""
    global _client
    if _client is None:
        if not DEEPSEEK_API_KEY:
            raise ValueError("DeepSeek API Key 未设置，请在 DEEPSEEK_API_KEY 变量中填入有效的 API Key")
        
        try:
            # 简化客户端初始化，只传入必要参数
            _client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL
            )
            print("DeepSeek 客户端初始化成功")
        except Exception as e:
            print(f"客户端初始化失败: {e}")
            raise
    return _client

def chat(messages):
    """
    通过 DeepSeek API 调用在线模型，返回流式生成器
    参数: messages - 聊天消息列表
    返回: generator - 流式传输的文本片段
    """
    # 限制消息历史长度，避免过长的上下文
    MAX_MESSAGES = 10
    if len(messages) > MAX_MESSAGES:
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        recent_messages = messages[-MAX_MESSAGES:]
        messages = system_messages + recent_messages
        print(f"消息历史被截断到 {len(messages)} 条")

    print(f"当前消息历史 (简略): {json.dumps(messages[-3:], ensure_ascii=False)}")

    try:
        # 获取 DeepSeek 客户端
        client = _get_deepseek_client()
        
        # --- 插入：在请求前加入 system prompt，限制回复长度 ---
        # 如果 messages 中已有 system 消息则不重复添加
        if any(m.get("role") == "system" for m in messages):
            local_messages = messages
        else:
            local_messages = [
                {"role": "system", "content": "You are a helpful assistant.If the user does not mention the word limit, please reply within 200 characters by default."}
            ] + messages
        # --- 插入结束 ---

        print(f"=== 发送流式聊天请求到 DeepSeek ===")
        start_time = time.time()

        # 调用 DeepSeek API，使用更保守的参数
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=local_messages,
            temperature=0.7,
            stream=True
        )

        total_content = ""
        chunk_count = 0
        content_received = False

        # 处理流式响应
        for chunk in response:
            # 检查 chunk 结构
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                    content = choice.delta.content
                    if content is not None:
                        content_received = True
                        total_content += content
                        chunk_count += 1
                        
                        print(f"收到文本片段 {chunk_count}: {repr(content[:50])}")
                        yield content
                
                # 检查是否完成
                if hasattr(choice, 'finish_reason') and choice.finish_reason is not None:
                    print(f"流式传输完成，原因: {choice.finish_reason}")
                    break

        elapsed = time.time() - start_time
        print(f"流式传输结束: chunks={chunk_count}, received={content_received}, len={len(total_content)}, time={elapsed:.2f}s")
        
        if not content_received:
            print("警告: 未收到任何内容")
            yield "抱歉，我现在无法正常回复，请稍后再试。"

    except ValueError as e:
        print(f"配置错误: {e}")
        yield f"配置错误: {str(e)}"
    except Exception as e:
        print(f"DeepSeek API 调用错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        yield f"错误: DeepSeek API 调用失败 - {str(e)}"