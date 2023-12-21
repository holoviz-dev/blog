---
title: "Panel AI Chatbot Tips: Memory and Downloadable Conversations,"
date: "2023-12-22"
description: ""
author:
  - Andrew Huang
  - Sophia Yang
categories: [showcase, panel, ai, llm, chatbot]
image: "images/chatbot.png"
---

In this post, we'll explore how to build a simple AI chatbot, enhance it with memory capabilities, and finally, implement a feature to download conversations for further fine-tuning.


- Getting started building a simple Mixtral AI chatbot (with no memory)
- Adding memory to manage chat histories 
- Adding download button to download all conversations 



# Getting started building a simple AI chatbot (with no memory)

## Mistral models

## OpenAI models

# Adding memory to manage chat histories 

## Mistral models 
```python

import os
import panel as pn
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

pn.extension()


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    model = "mistral-small"
    messages = [
        ChatMessage(role=message["role"], content=message["content"])
        for message in instance.serialize()[1:]
    ]
    print(messages)
    response = client.chat_stream(model=model, messages=messages)

    message = ""
    for chunk in response:
        part = chunk.choices[0].delta.content
        if part is not None:
            message += part
            yield message


client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
chat_interface = pn.chat.ChatInterface(callback=callback, callback_user="Mixtral")
chat_interface.send(
    "Send a message to get a reply from Mixtral!", user="System", respond=False
)
chat_interface.servable()
```


## OpenAI models
```python
"""
Demonstrates how to use the `ChatInterface` to create a chatbot using
OpenAI's with async/await.
"""

import panel as pn
from openai import AsyncOpenAI

pn.extension()


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    messages = instance.serialize()[1:]
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
    )
    message = ""
    async for chunk in response:
        part = chunk.choices[0].delta.content
        if part is not None:
            message += part
            yield message


aclient = AsyncOpenAI()
chat_interface = pn.chat.ChatInterface(callback=callback, callback_user="ChatGPT")
chat_interface.send(
    "Send a message to get a reply from ChatGPT!", user="System", respond=False
)
chat_interface.servable()
```

# Adding download button to download all conversations 
## Mistral models

## OpenAI models

```python
"""
Demonstrates how to use the `ChatInterface` to create a chatbot using
OpenAI's with async/await.
"""

import panel as pn
from openai import AsyncOpenAI
from io import StringIO
import json

pn.extension()


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    messages = instance.serialize()[1:]
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
    )
    message = ""
    async for chunk in response:
        part = chunk.choices[0].delta.content
        if part is not None:
            message += part
            yield message

def download_history():
   buf = StringIO()
   json.dump(chat_interface.serialize(), buf)
   buf.seek(0)
   return buf

file_download = pn.widgets.FileDownload(
   callback=download_history, filename="history.json"
)
header = pn.Row(pn.HSpacer(), file_download)

aclient = AsyncOpenAI()
chat_interface = pn.chat.ChatInterface(
    callback=callback, 
    callback_user="ChatGPT",
    header=header
    )
chat_interface.send(
    "Send a message to get a reply from ChatGPT!", user="System", respond=False
)
chat_interface.servable()
```

# Conclusion


If you are interested in learning more about how to build AI chatbot in Panel, please read our related blog posts: 

- [Build a Mixtral Chatbot with Panel](https://blog.holoviz.org/posts/mixtral/)
- [Building AI Chatbots with Mistral and Llama2](https://medium.com/@sophiamyang/building-ai-chatbots-with-mistral-and-llama2-9c0f5abc296c) 
- [Building a Retrieval Augmented Generation Chatbot](https://medium.com/@sophiamyang/building-a-retrieval-augmented-generation-chatbot-d567a24fcd14)
- [How to Build Your Own Panel AI Chatbots](https://medium.com/@sophiamyang/how-to-build-your-own-panel-ai-chatbots-ef764f7f114e)
- [Build a RAG chatbot to answer questions about Python libraries](https://blog.holoviz.org/posts/fleet_ai/)

If you find Panel useful, please consider giving us a star on Github ([https://github.com/holoviz/panel](https://github.com/holoviz/panel)). If you have any questions, feel free to ask on our [Discourse](https://discourse.holoviz.org/). Happy coding! 

