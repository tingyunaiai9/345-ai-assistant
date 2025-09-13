import gradio as gr
import os
import time
from chat import chat  # 导入chat函数
from tts import text2audio  # 导入TTS函数
from stt import audio2text  # 导入STT函数
from image_generate import image_generate  # 导入图片生成函数
import pdf  # 导入pdf.py中的函数
from search import search  # 导入search函数
from fetch import fetch  # 导入fetch函数
from function import function_calling, clear_todo  # 导入函数调用功能

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.
messages = []
current_file_text = None

def add_text(history, text):
    """
    添加用户输入的文本到对话历史
    """
    history = history + [(text, None)]
    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    """
    添加文件到对话历史，并处理txt文件归纳总结
    """
    global current_file_text, messages
    filename = file.name
    history = history + [((filename,), None)]

    # 判断是否为png图片
    if filename.endswith('.png'):
        # 先在聊天中显示图片
        # new_history = history.copy()
        # new_history[-1] = ((filename,), None)
        # yield new_history
        yield history
        try:
            from mnist import image_classification
            result = image_classification(file)
            print(f"图片分类结果: {result}")

            # 更新 messages
            messages.append({
                "role": "user",
                "content": f"Please classify {filename}"
            })

            messages.append({
                "role": "assistant",
                "content": f"Classification result: {result}"
            })

            # 聊天中显示：用户发送图片，AI回复分类结果
            result_history = history.copy()
            # 用户发图片（左侧），AI回复分类（右侧）
            result_history[-1] = ((filename,), f"Classification result: {result}")
            yield result_history
            return

        except Exception as e:
            print(f"图片分类出错: {e}")
            error_response = f"图片分类出错: {str(e)}"
            error_history = history.copy()
            error_history[-1] = ((filename,), error_response)
            yield error_history
            return

    # 判断是否为txt文件
    if filename.endswith('.txt'):
        try:
            # 读取文件内容
            with open(filename, 'r', encoding='utf-8') as f:
                current_file_text = f.read()

            print(f"读取txt文件: {filename}")
            print(f"文件内容长度: {len(current_file_text)} 字符")

            # 生成归纳总结prompt
            summary_prompt = pdf.generate_summary(current_file_text)

            # 更新messages
            messages.append({"role": "user", "content": summary_prompt})

            # 流式调用generate_text
            full_response = ""
            try:
                for chunk in pdf.generate_text(summary_prompt):
                    full_response += chunk
                    new_history = history.copy()
                    new_history[-1] = ((filename,), full_response)
                    yield new_history

                # 保存AI回复
                if full_response.strip():
                    messages.append({"role": "assistant", "content": full_response})
                    print(f"文件总结完成，回复长度: {len(full_response)} 字符")
                else:
                    print("警告: 文件总结没有返回内容")
                    new_history = history.copy()
                    new_history[-1] = ((filename,), "文件已上传，但总结功能暂时不可用")
                    yield new_history

            except Exception as e:
                print(f"文件总结过程中出错: {e}")
                error_response = f"文件总结出错: {str(e)}"
                new_history = history.copy()
                new_history[-1] = ((filename,), error_response)
                yield new_history

        except Exception as e:
            print(f"读取文件出错: {e}")
            error_response = f"读取文件出错: {str(e)}"
            new_history = history.copy()
            new_history[-1] = ((filename,), error_response)
            yield new_history
    
    elif filename.endswith(".wav"):
        try:
            print(f"检测到wav音频文件: {filename}")

            # 先显示音频文件
            audio_history = history.copy()
            audio_history[-1] = ((filename,), "正在音频转文字中……")
            yield audio_history

            # 调用语音转文字功能
            current_file_text = audio2text(filename)

            if current_file_text:
                print(f"语音转文字成功: {current_file_text}")

                # 将转换后的文字作为用户消息添加到messages
                messages.append({"role": "user", "content": current_file_text})
                print(f"已将语音转文字结果添加到messages，当前messages长度: {len(messages)}")

                # 显示语音转文字结果
                stt_history = history.copy()
                stt_history[-1] = (
                    (filename,),
                    f"🎤 语音转文字: {current_file_text}\n\n正在生成AI回复..."
                )
                yield stt_history

                # 调用chat函数获取AI回复
                full_response = ""
                try:
                    print("开始调用chat函数获取AI回复...")
                    chunk_count = 0
                    for chunk in chat(messages):
                        chunk_count += 1
                        full_response += chunk
                        print(f"收到第{chunk_count}个chunk，当前回复长度: {len(full_response)}")

                        new_history = history.copy()
                        display_text = f"🎤 语音转文字: {current_file_text}\n\nAI回复: {full_response}"
                        new_history[-1] = ((filename,), display_text)
                        yield new_history

                    print(f"chat函数调用完成，总共收到{chunk_count}个chunks")

                    # 保存AI回复到messages
                    if full_response.strip():
                        messages.append({"role": "assistant", "content": full_response})
                        print(f"音频处理完成，AI回复长度: {len(full_response)} 字符")
                        print(f"保存后messages长度: {len(messages)}")
                    else:
                        print("警告: AI没有返回有效回复")
                        new_history = history.copy()
                        new_history[-1] = (
                            (filename,),
                            f"🎤 语音转文字: {current_file_text}\n\n⚠️ AI回复异常",
                        )
                        yield new_history

                except Exception as e:
                    print(f"AI回复过程中出错: {type(e).__name__}: {e}")
                    import traceback
                    print("详细错误信息:")
                    traceback.print_exc()

                    error_response = (
                        f"🎤 语音转文字: {current_file_text}\n\n❌ AI回复出错: {str(e)}"
                    )
                    new_history = history.copy()
                    new_history[-1] = ((filename,), error_response)
                    yield new_history
            else:
                print("语音转文字失败")
                error_response = "❌ 语音转文字失败，请检查音频文件格式或网络连接"
                new_history = history.copy()
                new_history[-1] = ((filename,), error_response)
                yield new_history

        except Exception as e:
            print(f"处理音频文件出错: {type(e).__name__}: {e}")
            import traceback
            print("详细错误信息:")
            traceback.print_exc()

            error_response = f"❌ 处理音频文件出错: {str(e)}"
            new_history = history.copy()
            new_history[-1] = ((filename,), error_response)
            yield new_history
    else:
        # 其他文件直接返回
        new_history = history.copy()
        new_history[-1] = ((filename,), "已上传文件，但目前仅支持txt文件的归纳总结功能")
        yield new_history

def bot(history):
    """
    处理用户消息并生成AI回复（流式传输），支持/file content指令
    """
    global messages, current_file_text

    print(f"\n=== 开始处理新的用户消息 ===")
    print(f"当前history长度: {len(history)}")
    print(f"当前messages长度: {len(messages)}")

    # 获取最新的用户消息
    if not history or not history[-1][0]:
        print("错误: 没有找到用户消息")
        return

    user_message = history[-1][0]

    # 如果是文件上传消息，跳过处理
    if isinstance(user_message, tuple):
        print("检测到文件上传消息，跳过bot处理")
        return

    print(f"用户消息: {repr(user_message)}")

    # 检查是否为 /audio 指令 - 提前处理，单独逻辑
    if user_message.startswith('/audio '):
        actual_message = user_message[7:]  # 移除 "/audio " 前缀
        print(f"音频请求，实际消息: {repr(actual_message)}")
        
        # 将用户消息添加到messages
        messages.append({
            "role": "user",
            "content": actual_message
        })
        print(f"添加用户消息后，messages长度: {len(messages)}")

        # 显示处理状态
        history[-1] = (user_message, "🎵 正在生成语音回复...")
        yield history

        # 获取AI回复文本（不显示流式过程）
        full_response = ""
        try:
            print("开始调用chat函数获取AI回复...")
            for response_chunk in chat(messages):
                full_response += response_chunk

            # 保存AI回复到messages
            if full_response.strip():
                messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                print(f"AI回复完成，长度: {len(full_response)} 字符")

                # 生成音频文件
                try:
                    print("生成音频文件...")
                    audio_file = text2audio(full_response)
                    if audio_file and os.path.exists(audio_file):
                        print(f"音频文件生成成功: {audio_file}")
                        
                        # 只显示音频文件，不显示文字
                        final_history = history.copy()
                        final_history[-1] = (user_message, (audio_file,))
                        yield final_history
                    else:
                        print("音频文件生成失败")
                        error_history = history.copy()
                        error_history[-1] = (user_message, "❌ 音频生成失败")
                        yield error_history

                except Exception as e:
                    print(f"音频生成过程中出错: {e}")
                    error_history = history.copy()
                    error_history[-1] = (user_message, f"❌ 音频生成出错: {str(e)}")
                    yield error_history
            else:
                print("警告: AI没有返回有效回复")
                error_history = history.copy()
                error_history[-1] = (user_message, "❌ AI回复异常")
                yield error_history

        except Exception as e:
            print(f"AI回复过程中出错: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            error_history = history.copy()
            error_history[-1] = (user_message, f"❌ AI回复出错: {str(e)}")
            yield error_history

        print(f"=== 音频消息处理完成 ===\n")
        return

    # 检查是否为 /function 指令
    if user_message.startswith('/function '):
        print("检测到 /function 指令，正在执行函数调用...")
        content = user_message[10:].strip() # 提取 "/function " 后面的内容
        print(f"函数调用内容: {content}")

        # 构造函数调用消息
        function_call_messages = [{"role": "user", "content": content}]

        # 按照要求，更新messages时去掉/function
        messages.append({
            "role": "user",
            "content": content
        })
        print(f"添加用户消息后，messages长度: {len(messages)}")

        try:
            # 调用 function_calling 函数
            print(f"正在以隔离上下文调用 function_calling: {function_call_messages}")
            response = function_calling(function_call_messages)
            print(f"函数调用返回: {response}")

            # 将函数调用的结果显示在界面上
            history[-1] = (user_message, response)

            # 将函数调用的结果也存入messages，以便上下文连续
            messages.append({
                "role": "assistant",
                "content": response
            })
            print(f"保存回复后messages长度: {len(messages)}")

            yield history
            print(f"=== 函数调用处理完成 ===\n")
            return
        except Exception as e:
            if messages and messages[-1]["content"] == content:
                messages.pop()
                
            print(f"函数调用过程中出错: {e}")
            error_response = f"函数调用出错: {str(e)}"
            error_history = history.copy()
            error_history[-1] = (user_message, error_response)
            yield error_history
            return

    # 检查是否为 /file content 指令
    if user_message.startswith('/file '):
        content = user_message[6:].strip()
        print(f"收到/file指令，内容: {content}")

        if not current_file_text:
            error_history = history.copy()
            error_history[-1] = (user_message, "请先上传文件后再使用 /file 指令")
            yield error_history
            return

        try:
            # 生成结合文件内容的问题
            question = pdf.generate_question(current_file_text, content)
            print(f"生成的问题: {question[:100]}...")

            # 更新messages
            messages.append({"role": "user", "content": question})

            # 初始化回复
            history[-1] = (user_message, "")

            # 流式调用generate_text
            full_response = ""
            for chunk in pdf.generate_text(question):
                full_response += chunk
                new_history = history.copy()
                new_history[-1] = (user_message, full_response)
                yield new_history

            # 保存AI回复
            if full_response.strip():
                messages.append({"role": "assistant", "content": full_response})
                print(f"/file指令处理完成，回复长度: {len(full_response)} 字符")
            else:
                print("警告: /file指令没有返回内容")

        except Exception as e:
            print(f"/file指令处理出错: {e}")
            error_response = f"处理/file指令时出错: {str(e)}"
            error_history = history.copy()
            error_history[-1] = (user_message, error_response)
            yield error_history

        return

    is_search_request = user_message.startswith('/search ') # 检查是否是搜索请求
    is_fetch_request = user_message.startswith('/fetch ') # 检查是否是抓取请求
    is_image_request = user_message.startswith('/image ') # 检查是否是图片请求

    if is_search_request:
        print("检测到 /search 指令，正在执行网络搜索...")
        search_query = user_message[8:] # 提取 "/search " 后面的内容
        print(f"搜索查询: {search_query}")

        # 调用search函数，它会返回一个包含搜索结果的格式化提问
        content_for_llm = search(search_query)
        print(f"搜索后准备发送给LLM的内容:\n---\n{content_for_llm}\n---")

        # 如果search函数返回错误信息，则直接显示错误并终止
        if content_for_llm.startswith("错误：") or content_for_llm.startswith("An error"):
            print(f"搜索时发生错误: {content_for_llm}")
            history[-1] = (history[-1][0], content_for_llm)
            yield history
            return # 提前结束函数执行

        messages.append({
            "role": "user",
            "content": content_for_llm
        })
    elif is_image_request:
        actual_message = user_message[7:]
        print(f"图片请求，实际消息: {repr(actual_message)}")
        # 直接生成图片，不走 chat 流程
        try:
            print("开始调用 image_generate...")
            image_url = image_generate(actual_message)
            if image_url:
                reply = f"![]({image_url})"
                # 更新 messages 聊天记录
                messages.append({
                    "role": "user",
                    "content": user_message
                })
                messages.append({
                    "role": "assistant",
                    "content": image_url
                })
            else:
                reply = "图片生成失败，请稍后重试。"
            final_history = history.copy()
            final_history[-1] = (final_history[-1][0], reply)
            yield final_history
        except Exception as e:
            print(f"图片生成过程中出错: {e}")
            error_info = f"图片生成出错: {str(e)}"
            final_history = history.copy()
            final_history[-1] = (final_history[-1][0], error_info)
            yield final_history
        print(f"=== 图片消息处理完成 ===\n")
        return # 直接返回

    elif is_fetch_request:
        print("检测到 /fetch 指令，正在获取网页内容...")
        url = user_message[7:]  # 提取 "/fetch " 后面的URL
        print(f"要获取的URL: {url}")

        # 调用fetch函数，它会返回一个格式化的问题
        question = fetch(url)
        print(f"fetch函数返回的问题:\n---\n{question}\n---")

        # 如果fetch函数返回错误信息，则直接显示错误并终止
        if question.startswith("Error:"):
            print(f"获取网页时发生错误: {question}")
            history[-1] = (history[-1][0], question)
            yield history
            return  # 提前结束函数执行

        # 将fetch结果作为用户消息内容传递给LLM
        messages.append({
            "role": "user",
            "content": question
        })
    else:
        actual_message = user_message

    # 将用户消息添加到messages列表（只有在不是search或fetch请求时才添加原始消息）
    if not is_search_request and not is_fetch_request:
        messages.append({
            "role": "user",
            "content": actual_message
        })
    print(f"添加用户消息后，messages长度: {len(messages)}")

    # 初始化AI回复
    history[-1] = (history[-1][0], "")

    # 调用chat函数获取流式AI回复
    full_response = ""
    chunk_count = 0
    last_update_time = time.time()

    try:
        print("开始调用chat函数...")
        for response_chunk in chat(messages):
            chunk_count += 1
            full_response += response_chunk

            # 创建新的history副本，避免引用问题
            new_history = history.copy()
            new_history[-1] = (new_history[-1][0], full_response)

            current_time = time.time()
            if current_time - last_update_time >= 0.1:  # 每0.1秒更新一次界面
                print(f"更新界面，块 {chunk_count}，当前长度: {len(full_response)}")
                last_update_time = current_time

            yield new_history

    except Exception as e:
        print(f"流式传输过程中出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

        error_history = history.copy()
        error_history[-1] = (error_history[-1][0], f"错误: {str(e)}")
        yield error_history
        return

    # 流式传输完成后的处理
    if full_response.strip():
        # 将完整回复添加到messages列表
        messages.append({
            "role": "assistant",
            "content": full_response
        })
        print(f"完整回复已保存到messages: {len(full_response)} 字符")
        print(f"保存后messages长度: {len(messages)}")
        print(f"回复内容: {repr(full_response)}")

    else:
        print("警告: 没有收到有效回复，不添加到messages")

    print(f"=== 消息处理完成 ===\n")

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
        height=500,
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, type '/audio your question' for audio reply, or '/file your question' to ask about uploaded file, '/search query' for web search, '/fetch url' for webpage summary, '/image content' for image generation",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    # 绑定事件处理函数（支持流式传输）
    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=True).then(
        bot, chatbot, chatbot  # bot函数现在返回generator，支持流式更新
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=True)

    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=True)

    # 清除按钮功能
    def clear_chat():
        global messages, current_file_text
        messages = []
        current_file_text = None
        clear_todo()
        print("=== 聊天记录和文件内容已清除 ===")
        return []

    clear_btn.click(clear_chat, None, [chatbot], queue=False)

demo.queue()
demo.launch()
