import json
import requests
from openai import OpenAI
from typing import List, Dict

# 你需要从和风天气等天气服务提供商获取API密钥，并将其设置为环境变量
# 例如: export QWEATHER_API_KEY='your_key_here'
API_HOST = "ka564u5vb4.re.qweatherapi.com"  # 您的API Host
JWT_TOKEN = "" # 请在这里填入你的 JWT 身份认证 token
CITY_LOOKUP_URL = f"https://{API_HOST}/geo/v2/city/lookup"
WEATHER_NOW_URL = f"https://{API_HOST}/v7/weather/now"

TODO_LIST: List[str] = []

def clear_todo() -> None:
    '''
    清空代办事项列表
    '''
    global TODO_LIST
    TODO_LIST = []
    print("=== 待办事项列表已清空 ===")

def lookup_location_id(location: str) -> str | None:
    """
    调用城市搜索API，返回第一个匹配的location_id。

    Args:
        location: 要查询的城市名称，例如 "Beijing"。

    Returns:
        如果找到，则返回城市的location_id；否则返回None。
    """
    if not JWT_TOKEN or JWT_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("错误：JWT_TOKEN 未设置或未替换为实际token。")
        print("请将 JWT_TOKEN 变量设置为您的实际JWT身份认证token。")
        return None

    try:
        # 使用Bearer token认证方式，按照文档要求
        headers = {
            'Authorization': f'Bearer {JWT_TOKEN}'
        }
        params = {
            'location': location
        }

        response = requests.get(CITY_LOOKUP_URL, headers=headers, params=params)
        response.raise_for_status()  # 如果请求失败（例如4xx或5xx），则会引发HTTPError
        data = response.json()

        # API返回状态码"200"表示成功，并检查location列表是否为空
        if data.get("code") == "200" and data.get("location"):
            # 按照要求，返回第一个地理位置的ID
            return data["location"][0]["id"]
        else:
            print(f"未能找到地点 '{location}' 的ID。API响应: {data.get('code')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"调用城市搜索API时出错: {e}")
        return None
    except (KeyError, IndexError):
        # 处理JSON结构不符合预期或'location'列表为空的情况
        print(f"API响应格式不正确或未找到地点 '{location}'。")
        return None


def get_current_weather(location: str) -> str | None:
    """
    获取指定地点的实时天气信息。
    它首先查找地点ID，然后查询该ID的当前天气。

    Args:
        location: 要查询的城市名称，例如 "Beijing"。

    Returns:
        格式化的天气信息字符串，或在失败时返回None。
    """
    location_id = lookup_location_id(location)
    if not location_id:
        return None

    if not JWT_TOKEN or JWT_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("错误：JWT_TOKEN 未设置或未替换为实际token。")
        return None

    try:
        headers = {'Authorization': f'Bearer {JWT_TOKEN}'}
        params = {'location': location_id}
        response = requests.get(WEATHER_NOW_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "200" and data.get("now"):
            now_data = data["now"]
            feelsLike = now_data.get("feelsLike", "N/A")
            text = now_data.get("text", "N/A")
            humidity = now_data.get("humidity", "N/A")
            return f"Temperature: {feelsLike} Description: {text} Humidity: {humidity}"
        else:
            print(f"获取天气失败 for location ID '{location_id}'. API 响应: {data.get('code')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"调用实时天气API时出错: {e}")
        return None
    except KeyError:
        print("API响应格式不正确或缺少天气数据。")
        return None

def add_todo(todo: str) -> str:
    """
    将一个待办事项添加到全局列表中，并以指定格式返回整个列表。

    Args:
        todo: 要添加的待办事项，例如 "walk"。

    Returns:
        一个多行字符串，列出了所有待办事项。
    """
    TODO_LIST.append(todo)
    # 根据功能说明，格式化输出，每个TODO项占一行，以'- '开头
    formatted_list = [f"- {item}" for item in TODO_LIST]
    return "\n".join(formatted_list)

def function_calling(messages: List[Dict]) -> str:
    """
    模拟语言模型来解析用户意图、调用相应的函数并返回结果。

    Args:
        messages: 聊天消息列表。

    Returns:
        一个字符串，其中包含调用函数后的结果。
    """
    try:
        client = OpenAI(
            base_url="http://localhost:8080/v1",
            api_key="not-needed-for-localai" # 本地服务通常不需要API Key
        )
    
        tools_definitions = [
            {
                "name": "get_current_weather",
                "description": "get the weather of the location user mentioned",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "the city or region that user mentioned",
                        }
                    },
                    "required": ["location"],
                },
            },
            {
                "name": "add_todo",
                "description": "add a new item in todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "todo": {
                            "type": "string",
                            "description": "the item need to be added",
                        }
                    },
                    "required": ["todo"],
                },
            },
        ]

        print(f"[Orchestrator] 正在向模型发送消息: '{messages[-1]['content']}'")

        response = client.chat.completions.create(
            model="ggml-openllama.bin",  # 确保你本地加载的模型支持函数调用
            messages=messages,
            functions=tools_definitions,
        )
        message = response.choices[0].message

        # 检查消息是否包含函数调用
        if message.function_call:
            function_name = message.function_call.name
            
            print(f"[Orchestrator] 模型决定调用函数: {function_name}")
            
            try:
                function_args = json.loads(message.function_call.arguments)
                print(f"[Orchestrator] 函数参数: {function_args}")
            except json.JSONDecodeError:
                error_msg = f"错误：模型返回了无效的参数JSON: {message.function_call.arguments}"
                print(error_msg)
                return error_msg

            # 将函数名映射到实际的Python函数对象
            available_functions = {
                "get_current_weather": get_current_weather,
                "add_todo": add_todo,
            }
            
            function_to_call = available_functions.get(function_name)

            if function_to_call:
                # 使用 **kwargs 将字典解包为关键字参数来调用函数
                return function_to_call(**function_args)
            else:
                return f"错误：模型尝试调用一个未知的函数: {function_name}"
        else:
            # 如果模型没有调用函数，直接返回其文本回复
            print("[Orchestrator] 模型选择直接回复。")
            return message.content or "模型未返回有效回复"
    except Exception as e:
        error_msg = f"在函数调用过程中发生错误: {e}"
        print(error_msg)
        return error_msg


if __name__ == "__main__":
    '''
    Since we are using an earlier version of the OpenAI package, the function call is slightly different from the current documentation.
    An example of the `tools` parameter for function calling:
    tools = [
        {
            "name": "get_current_weather",
            "description": "Return the temperature of the region specified by the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "User specified region",
                    },
                },
                "required": ["location"],
            },
        },
    ]
    '''
    print("--- 测试天气功能 ---")
    weather_messages = [{"role": "user", "content": "What's the weather like in Beijing?"}]
    print(f"用户: {weather_messages[0]['content']}")
    response = function_calling(weather_messages)
    print(f"模型输出:\n{response}\n")

    print("--- 测试TODO功能 ---")
    todo_messages_1 = [{"role": "user", "content": "Add a todo: walk"}]
    print(f"用户: {todo_messages_1[0]['content']}")
    response = function_calling(todo_messages_1)
    print(f"模型输出:\n{response}\n")

    todo_messages_2 = [{"role": "user", "content": "Add a todo: swim"}]
    print(f"用户: {todo_messages_2[0]['content']}")
    response = function_calling(todo_messages_2)
    print(f"模型输出:\n{response}\n")
