import requests
import os

def audio2text(file):
    """
    将音频文件转换为文字内容
    
    Args:
        file (str): 音频文件路径（wav格式）
        
    Returns:
        str: 转换后的文字内容，如果失败则返回 None
    """
    try:
        # LocalAI STT API 端点
        api_url = "http://localhost:8080/v1/audio/transcriptions"
        
        # 检查文件是否存在
        if not os.path.exists(file):
            print(f"错误: 文件不存在 {file}")
            return None
        
        # 准备文件和数据
        with open(file, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(file), audio_file, 'audio/wav')
            }
            data = {
                'model': 'whisper-1'  
            }
            
            # 发送 POST 请求
            response = requests.post(api_url, files=files, data=data)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '')
            return text
        else:
            print(f"API 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

if __name__ == "__main__":
    result = audio2text('sun-wukong.wav')
    if result:
        print(f"转换结果: {result}")
    else:
        print("转换失败！")