import requests
from bs4 import BeautifulSoup

def fetch(url: str):
    """
    Fetches the content from a given URL, extracts text from <p> tags,
    and formats it into a question for a language model.
    """
    try:
        # 1. 发送HTTP请求获取网页内容
        response = requests.get(url, timeout=10)
        # 如果请求不成功，会引发HTTPError
        response.raise_for_status() 
        
        # 2. 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取第二个<p>标签的文本内容
        p_tags = soup.find_all('p')
        
        if len(p_tags) >= 2:
            processed_results = p_tags[1].get_text().strip()  # 索引1表示第二个
        elif len(p_tags) == 1:
            processed_results = "只找到一个<p>标签，没有第二个"
        else:
            processed_results = "未找到任何<p>标签内容"
        
        # 3. 格式化提取出的文本，形成一个有效的提问
        question = f"Please provide a 20-word summary of the website {url} based on this content:\n\n{processed_results}\n\nSummary:"
        
        return question

    except requests.exceptions.RequestException as e:
        # 捕获网络请求错误（如连接失败、超时等）
        return f"Error: Failed to retrieve the webpage. Details: {e}"
    except Exception as e:
        # 捕获其他可能的错误
        return f"Error: An unexpected error occurred. Details: {e}"

if __name__ == "__main__":
    # 使用提供的示例URL进行测试
    test_url = "https://dev.qweather.com/en/help"
    question_result = fetch(test_url)
    
    if question_result.startswith("Error:"):
        print(question_result)
    else:
        print("Successfully generated question:")
        print("---")
        print(question_result)
        print("---")