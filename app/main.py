import json
import os
import sys
from fastapi import Depends, FastAPI
from groq import Groq
from app.models import models
from app.classes.classes import MessageRequest, User
from app.environments import LLMODEL, LUNA_DEV_KEY
from app.constants.messages import messages
from app.constants.tools import tools
from app.auth.auth import router as auth_router, validate_token
from app.database.database import engine

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title='Luna API', root_path='/api')

app.include_router(auth_router, prefix='/auth')

client = Groq(api_key=LUNA_DEV_KEY)

# create tables if doesn't exist yet
models.Base.metadata.create_all(bind=engine)

def save_info():
    print("\n\nsave info into db line 20")

    return json.dumps({"message": "Informação salva com sucesso"})


@app.post("/chat-luna")
async def chatLuna(request: MessageRequest,current_user: User = Depends(validate_token)):

    user_name=current_user.name
    message = request.message

    messages.append({"role": "system", "content": "Antes de qualquer coisa, dê boas vindas ao usuário falando o nome dele: " + user_name})
    messages.append({"role": "user", "content": message})

    completion = client.chat.completions.create(
        model=LLMODEL,
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

    second_completion = client.chat.completions.create(model=LLMODEL, messages=messages)
    return second_completion.choices[0].message.content


@app.get("/")
async def helloWorld():
    return {"message": "Hello World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)