# ai-assistant-2025

请按照网络学堂-课程文件当中的大作业文档完成大作业。如有任何问题，请在网络学堂讨论区的大作业讨论贴中发贴求助，请在你的贴子中详细描述你遇到的问题、环境配置情况，以及完整的报错信息。



后续成绩复议等问题可以联系助教：

熊翊哲 xiongyizhe2001@163.com


## 运行说明

### API Key

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
  
  
