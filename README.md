# 三四五：基于大模型的 AI 助手

清华大学软件学院2025夏《程序设计实践》课程

三四五组大作业：基于大模型的 AI 助手

## 一、项目介绍

本项目构建了一个多模态 AI 助手。助手能够支持文本聊天、图片生成、语音交互、网页总结、文件问答、函数调用以及图像分类等功能，结合 LocalAI 提供的 API，实现本地化、可交互的智能助手系统。

## 二、环境配置与运行方式

### 2.1 启动 LocalAI 模型服务

1. 将仓库 clone 到本地

2. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

3. 下载[模型文件](https://cloud.tsinghua.edu.cn/f/690d4fe1fab241268d56/?dl=1)并解压至 LocalAI/models 文件夹

4. 运行各个模型

   ```bash
   cd LocalAI
   docker compose up -d --pull always
   ```

* 默认接口地址为 http://localhost:8080。可通过以下命令检测：

  ```bash
  curl http://localhost:8080/models
  ```

### 2.2 安装 Python 依赖

建议使用 Conda 管理环境

```bash
conda create -n ai-assistant python=3.12
conda activate ai-assistant
pip install -r requirements.txt
```

### 2.3 配置 API Key

* 在 `chat.py` 的第 8 行，填入你的 DeepSeek API Key

  ```python
  # DeepSeek API 配置
  DEEPSEEK_API_KEY = (
      ""  # 请在这里填入你的 DeepSeek API Key
  )
  DEEPSEEK_BASE_URL = "https://api.deepseek.com"
  ```

* 在 `search.py` 的第 11 行，填入你的 API Key

  ```python
  def search(content: str, max_words: int = 80) -> str:
      """
      使用 SerpApi 的必应搜索接口对 content 进行搜索，仅取第一条 organic result 的 snippet，
      并将其与 content 组合成“有效提问”字符串返回（用于 messages 中的 user.content）。
      注意：不修改界面 history 的显示。
      """
      api_key = "" # 请在这里填入你的 SerpApi API Key，或设置环境变量 SERPAPI_API_KEY
      if not api_key:
          return "错误：SerpApi API 密钥尚未配置。请设置环境变量 SERPAPI_API_KEY。"
  ```


* 在 `function.py` 的第 9 行，填入你的 API Key

  - API的申请根据[API Host | 和风天气开发服务](https://dev.qweather.com/docs/configuration/api-host/)网站指导进行操作
  
  - 而JWT身份认证的过程较为繁琐，请根据[身份认证 | 和风天气开发服务](https://dev.qweather.com/docs/configuration/authentication/)网站指导进行操作，得到您的项目凭据和项目ID后，填入`generate_JWT.py`中的相应位置进行JWT身份认证的生成。
  
    - 运行`generate_JWT.py`前，须运行以下命令。
  
    ```cmd
    pip install pyjwt[crypto] cryptography
    ```
  完成后填入如下相应位置即可
  ```python
  # 你需要从和风天气等天气服务提供商获取API密钥，并将其设置为环境变量
  # 例如: export QWEATHER_API_KEY='your_key_here'
  API_HOST = "ka564u5vb4.re.qweatherapi.com"  # 您的API Host
  JWT_TOKEN = "" # 请在这里填入你的 JWT 身份认证 token
  CITY_LOOKUP_URL = f"https://{API_HOST}/geo/v2/city/lookup"
  WEATHER_NOW_URL = f"https://{API_HOST}/v7/weather/now"
  ```
  

### 2.4 配置 LeNet 模型

将 lenet 模型参数文件放在目录下，修改 `mnist.py` 中的模型路径

### 2.5 启动 AI 助手

```bash
python app.py
```

打开命令行输出的链接（一般为 http://127.0.0.1:7860）即可访问助手界面。

## 三、实现功能

**正常聊天**：调用大语言模型（deepseek）进行多轮对话。

**流式传输**：边生成边显示，提高交互体验。

**网络搜索**：通过 `/search content` 获取实时搜索结果并回答。

**网页总结**：通过 `/fetch url` 提取网页内容并生成摘要。

**图片生成**：通过 `/image prompt` 使用 Stable Diffusion 生成图片。

**语音输入**：上传 `.wav` 文件，实现语音转文字。

**语音输出**：通过 `/audio content` 生成语音回答。

**文件聊天**：上传 `.txt` 文件，支持总结与基于文件的问答。

**函数调用**：

- `/function What’s the weather like in Beijing?` → 获取实时天气
- `/function Add a todo: walk` → 管理 TODO 列表

**图片分类**：上传 `.png` 文件，使用 LeNet 对手写数字进行分类。
