import os


def image_generate(content: str):
    """
    TODO
    调用 stablediffusion API 生成图片并返回图片地址
    """
    import requests
    api_url = "http://localhost:8080/v1/images/generations"
    payload = {
        "prompt": content,
        "size": "256x256"
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        # 假设返回格式为 {"data": [{"url": "..."}]}
        image_url = data["data"][0]["url"]
        print("图片生成成功")
        return image_url
    except Exception as e:
        print(f"图片生成失败: {e}")
        return None

if __name__ == "__main__":
    image_generate('A cute baby sea otter')
