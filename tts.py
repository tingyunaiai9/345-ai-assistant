import requests
import os
from datetime import datetime

def text2audio(content: str):
    """
    将文本转换为音频文件
    
    Args:
        content (str): 要转换的文本内容
        
    Returns:
        str: 保存的音频文件路径，如果失败则返回 None
    """
    try:
        # LocalAI TTS API 端点
        api_url = "http://localhost:8080/tts"

        # 准备请求数据
        data = {
            "model": "en-us-blizzard_lessac-medium.onnx",  # 或者使用其他可用的 TTS 模型
            "input": content,
        }

        # 发送 POST 请求
        response = requests.post(api_url, json=data)

        # 检查响应状态
        if response.status_code == 200:
            # 创建音频文件目录
            audio_dir = "audio_output"
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)

            # 生成唯一的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_{timestamp}.wav"
            filepath = os.path.join(audio_dir, filename)

            # 保存音频文件
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"音频文件已保存到: {filepath}")
            return filepath
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
    result = text2audio("Sun Wukong (also known as the Great Sage of Qi Tian, Sun Xing Shi, and Dou Sheng Fu) is one of the main characters in the classical Chinese novel Journey to the West")
    if result:
        print(f"转换成功！文件路径: {result}")
    else:
        print("转换失败！")
