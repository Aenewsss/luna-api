import json
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from groq import Groq
from classes import MessageRequest
from starlette.responses import StreamingResponse
from messages import messages
from tools import tools

load_dotenv()

app = FastAPI()

LUNA_DEV_KEY = os.getenv("LUNA_DEV_KEY")
client = Groq(api_key=LUNA_DEV_KEY)
MODEL = "llama3-8b-8192"


def save_info():
    print("\n\nsave info into db")
    return json.dumps({"message": "Informação salva com sucesso"})


@app.post("/chat-luna")
async def chatLuna(request: MessageRequest):

    message = request.message
    print("message:", message)

    messages.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        temperature=1,
        max_tokens=1024,
        stop=None,
        tool_choice="auto",
    )

    tool_calls = completion.choices[0].message.tool_calls

    if tool_calls:
        available_functions = {
            "save_info": save_info,
        }
        for tool_call in tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            function = available_functions[name]

            print("89:", arguments)
            response = function()
            messages.append(
                {
                    "content": response,
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                }
            )

    second_completion = client.chat.completions.create(model=MODEL, messages=messages)
    return second_completion.choices[0].message.content


@app.get("/")
async def helloWorld():
    return {"message": "Hello World!"}
