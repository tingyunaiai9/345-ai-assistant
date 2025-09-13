import os
import re
from serpapi import GoogleSearch

def search(content: str, max_words: int = 80) -> str:
    """
    使用 SerpApi 的必应搜索接口对 content 进行搜索，仅取第一条 organic result 的 snippet，
    并将其与 content 组合成“有效提问”字符串返回（用于 messages 中的 user.content）。
    注意：不修改界面 history 的显示。
    """
    api_key = "" # 请在这里填入你的 SerpApi API Key，或设置环境变量 SERPAPI_API_KEY
    if not api_key:
        return "错误：SerpApi API 密钥尚未配置。请设置环境变量 SERPAPI_API_KEY。"

    query = content.strip()
    is_english = bool(re.search(r'[A-Za-z]', query))

    params = {
        "engine": "bing",
        "q": query,
        "api_key": api_key,
        "mkt": "en-US" if is_english else "zh-CN",
        "setlang": "en" if is_english else "zh-Hans",
        "bing_domain": "bing.com",
        "count": 1,         # 只要第一条，减少响应负担
        "safe": "active"
    }

    try:
        client = GoogleSearch(params)
        results = client.get_dict()

        org = results.get("organic_results") or []
        snippet = ""
        source_link = None
        if org:
            first = org[0]
            snippet = (first.get("snippet") or "").strip()
            source_link = first.get("link")

        # 组织“有效提问”（不是简单拼接）
        if is_english:
            # 英文提示
            prompt = (
                f"Answer the question using ONLY the following search snippet. "
                f"If the snippet is insufficient, explicitly say 'Insufficient information'. "
                f"Limit your answer to {max_words} words.\n\n"
                f"Question: {query}\n"
                f"Search snippet: {snippet or '[no snippet available]'}"
            )
            if source_link:
                prompt += f"\nSource: {source_link}"
        else:
            # 中文提示
            prompt = (
                f"请仅依据下方搜索摘要作答；若信息不足，请明确回复“信息不足”。"
                f"将回答限制在 {max_words} 词以内。\n\n"
                f"问题：{query}\n"
                f"搜索摘要：{snippet or '[暂无摘要]'}"
            )
            if source_link:
                prompt += f"\n来源：{source_link}"

        return prompt

    except Exception as e:
        return f"An error occurred during the search: {e}"
    
if __name__ == "__main__":
    # 这是当您直接运行 search.py 文件时的测试代码
    # 这里的 content 相当于用户在指令 "/search" 后面输入的内容
    
    # 示例1: 查询泰勒·斯威夫特
    print("--- 示例 1: 查询泰勒·斯威夫特 ---")
    query_taylor_swift = "who is Taylor Swift?"
    processed_content_ts = search(query_taylor_swift)
    print(processed_content_ts)

    print("\n" + "="*40 + "\n")

    # 示例2: 查询一个可能没有结果的随机字符串
    print("--- 示例 2: 查询一个无效内容 ---")
    query_random = "asdfqwerlkjhasdflkjh"
    processed_content_random = search(query_random)
    print(processed_content_random)