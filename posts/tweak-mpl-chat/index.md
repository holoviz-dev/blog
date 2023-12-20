---
title: "Build a AI Chatbot to Run Code and Tweak plots"
date: "2023-12-22"
description: "Powered by Panel and Mixtral 8x7B"
author:
  - Andrew Huang
  - Sophia Yang
categories: [showcase, panel, ai, llm, chatbot]
image: "images/chatbot.png"
---


Do you use Python to visualize data? Wouldn't it be nice if an AI chatbot can help you write Python code and improve your visualization automatically? 

In this blog post, we will build such an AI chatbot with Panel and Mixtral 8x7b that will help you generate code and execute code to tweak an Matplotlib plot. It has two functionalities:

1. You can chat with the AI assistant to do small tweaks of a Matplotlib plot or ask it to "make this figure ready for a poster presentation". This is especially helpful when we need help with styling but don't know where to start. This AI chatbot will not only generate ideas, but also runnable code to improve your plot directly. 

<img src="./images/app1.gif" width="100%" style="margin-left: auto; margin-right: auto; display: block;"></img>


2. You can also check the code of a figure, edit the code directly, and get the updated version of the plot. This is helpful when you would like to start with your own plot. You can copy and paste the code of your own plot here as a starting point for AI to improve. 

<img src="./images/app2.gif" width="100%" style="margin-left: auto; margin-right: auto; display: block;"></img>


# Hosted App and Code 

- Try out the app [here](https://huggingface.co/spaces/ahuang11/tweak-mpl-chat) (we will keep this app live for a week)
- Check the code [here](https://huggingface.co/spaces/ahuang11/tweak-mpl-chat/blob/main/app.py)


# How to make this chatbot? 

Before we get started, let's first generate a Mistral API from [https://console.mistral.ai/users/api-keys/](https://console.mistral.ai/users/api-keys/):

<img src="./images/mistral_api.png" width="100%" style="margin-left: auto; margin-right: auto; display: block;"></img> 

Once you have generated a key, make sure to save it as an environment variable with `export MISTRAL_API_KEY="TYPE YOUR API KEY"`. 

There are three chat endpoints with the Mistral API:

- Mistral-tiny: Mistral 7B Instruct v0.2, a better fine
tuning of the initial Mistral-7B
- Mistral-small:  Mixtral 8x7B, mastering multiple languages and code
- Mistral-medium: a top serviced model, outperforming GPT3.5

Both Mistral-small and Mistral-medium are much better at generating code than Mistral-tiny. Mistral-small responds faster and cheaper, so we will use Mistral-small. But if output quality is your priority, we definitely recommend Mistral-medium, as it generates the best code responses. 

## Step 1: Define default behaviors 

## Step 2: Define the `callback` function

## Step 3: Define the `ChatInterface`

## Step 4: Define other widgets

## Step 5: Define layout 


# Conclusion



If you are interested in learning more about how to build AI chatbot in Panel, please read our related blog posts: 

- [Building AI Chatbots with Mistral and Llama2](https://medium.com/@sophiamyang/building-ai-chatbots-with-mistral-and-llama2-9c0f5abc296c) 
- [Building a Retrieval Augmented Generation Chatbot](https://medium.com/@sophiamyang/building-a-retrieval-augmented-generation-chatbot-d567a24fcd14)
- [How to Build Your Own Panel AI Chatbots](https://medium.com/@sophiamyang/how-to-build-your-own-panel-ai-chatbots-ef764f7f114e)
- [Build a RAG chatbot to answer questions about Python libraries](https://blog.holoviz.org/posts/fleet_ai/)

If you find Panel useful, please consider giving us a star on Github ([https://github.com/holoviz/panel](https://github.com/holoviz/panel)). Happy coding! 
