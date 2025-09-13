import requests
import json
import time
from chat import chat  # 使用已验证可用的 chat 函数

def generate_text(prompt):
    """
    流式生成：将 prompt 包装为一个简单的 user 消息，调用已可用的 chat() 流式接口并逐块 yield。
    参数: prompt (str)
    返回: yield 字符串块（stream）
    """
    print("=== pdf.generate_text 调用 ===")
    print(f"Prompt内容: {prompt[:200]}...")
    try:
        chat_messages = [{"role": "user", "content": prompt}]
        chunk_count = 0
        for chunk in chat(chat_messages):
            chunk_count += 1
            # 直接 yield chunk（chat 已生成字符串分片）
            print(f"pdf.generate_text 收到 chunk {chunk_count}: {repr(chunk[:80])}")
            yield chunk
        print(f"pdf.generate_text 完成，共 {chunk_count} 个 chunk")
    except Exception as e:
        print(f"pdf.generate_text 异常: {e}")
        yield f"错误: {str(e)}"

def generate_summary(current_file_text):
    """
    根据文件内容生成 summary_prompt（用于传入文字补全接口）
    返回: summary_prompt (str)
    """
    print("=== pdf.generate_summary 调用 ===")
    # 简洁明确的 prompt，减少上下文依赖
    summary_prompt = f"Please summarize this text in 2-3 concise sentences:\n\n{current_file_text}"
    print(f"生成 summary_prompt 长度: {len(summary_prompt)}")
    return summary_prompt

def generate_question(current_file_text, content):
    """
    将 current_file_text 与用户输入 content 组合为一个有效问题 prompt
    返回: question (str)
    """
    print("=== pdf.generate_question 调用 ===")
    question = f"Based on the following text:\n{current_file_text}\n\nQuestion: {content}\n\nAnswer concisely:"
    print(f"生成 question 长度: {len(question)}")
    return question

# 简单测试（仅当直接运行 pdf.py 时）
if __name__ == "__main__":
    test_text = "Peter Parker, a brilliant but socially awkward teenager, gains spider-like abilities after a radioactive spider bite."
    p = generate_summary(test_text)
    print("测试 summary_prompt:", p)
    parts = []
    for i, chunk in enumerate(generate_text(p)):
        parts.append(chunk)
        print(f"测试收到 chunk {i+1}: {repr(chunk)}")
        if i >= 9:
            break
    print("测试完整响应预览:", "".join(parts)[:300])
