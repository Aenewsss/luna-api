import json
import os
import sys
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from groq import Groq
from requests import Session
from app.info.info import get_all_info, save_info
from app.models import models
from app.classes.classes import InfoCreate, MessageRequest, User
from app.environments import LLMODEL, LUNA_DEV_KEY
from app.constants.messages import messages
from app.constants.tools import tools
from app.constants.available_functions import available_functions
from app.auth.auth import router as auth_router, validate_token
from app.database.database import engine, get_db
from app.middlewares.user import UserMiddleware

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Luna API", root_path="/api")

app.include_router(auth_router, prefix="/auth")

client = Groq(api_key=LUNA_DEV_KEY)

# create tables if doesn't exist yet
models.Base.metadata.create_all(bind=engine)

app.add_middleware(UserMiddleware)

@app.get("/")
async def hello_world():
    print("\nline 207\n")
    return {"message": "Hello World!"}

@app.get("/webhook")
async def wpp_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print('\nmode, token, challenge', mode, token, challenge)
    
    if mode and token:
        if mode == "subscribe" and token == "my_custom_verify_token":
            return PlainTextResponse(challenge)
        else:
            return JSONResponse(content={"error": "Forbidden"}, status_code=403)

    return {"message": "Webhook called"}

@app.post("/chat-luna")
async def chatLuna(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.json()
    print('body 2', body)
    
    print('here 58',request.message)
    user_id = request.state.user_id
    user_name = request.state.user_name
    print('here 61',user_id, user_name, request.state)

    user_message = request.message

    messages.append(
        {
            "role": "system",
            "content": "Antes de qualquer coisa, dê boas vindas ao usuário falando o nome dele: "
            + user_name,
        }
    )
    messages.append({"role": "user", "content": user_message})

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

    if tool_calls == None:
        return completion.choices[0].message.content
    else:
        for tool_call in tool_calls:
            name = tool_call.function.name

            print("\nline 68", name)

            if name == "save_info":
                return flow_save_info(
                    tool_call_id=tool_call.id,
                    arguments=json.loads(tool_call.function.arguments),
                    name=name,
                    user_id=user_id,
                    user_message=user_message,
                    db=db,
                )
            elif name == "get_all_info":
                return flow_get_all_info(name=name, user_id=user_id, db=db)
            elif name == "remove_info":
                return flow_remove_info(
                    tool_call_id=tool_call.id, name=name, user_id=user_id, db=db
                )


def chat_to_save_data(user_id: int, user_message: str, db: Session):
    completion = client.chat.completions.create(
        model=LLMODEL,
        messages=[
            {
                "role": "system",
                "content": "Crie um objeto json com os dados: title={'título da informação que o usuário quer salvar'} e content={'conteúdo com a informação que o usuário quer salvar'}",
            },
            {
                "role": "system",
                "content": "Quando alguém pedir para você salvar alguma informação, você vai separar os dados da seguinte forma: title={'aqui vem o título que marca a informação principal'};content={'conteúdo em string com a informação que o usuário quer salvar'} e usar os dados resgatados da função save_info definida em suas tools para trazer a mensagem de retorno.",
            },
            {"role": "user", "content": user_message},
        ],
        tools=tools,
    )

    tool_calls = completion.choices[0].message.tool_calls

    if tool_calls:
        for tool_call in tool_calls:
            arguments = json.loads(tool_call.function.arguments)

            if "title" not in arguments or "content" not in arguments:
                return chat_to_save_data(user_id, user_message, db)
            else:
                title = arguments["title"]
                content = arguments["content"]

                name = tool_call.function.name
                function = available_functions[name]
                response = function(
                    InfoCreate(user_id=user_id, title=title, content=content), db
                )
                messages.append(
                    {
                        "content": response,
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                    }
                )

                second_completion = client.chat.completions.create(
                    model=LLMODEL, messages=messages
                )
                return second_completion.choices[0].message.content


def flow_save_info(
    tool_call_id, arguments, name, user_id: int, user_message: str, db: Session
):
    if "title" not in arguments or "content" not in arguments:
        return chat_to_save_data(user_id, user_message, db)
    else:
        title = arguments["title"]
        content = arguments["content"]
        function = available_functions[name]

        response = function(
            InfoCreate(user_id=user_id, title=title, content=content), db
        )

        return final_tool_message(response, tool_call_id, name)


def flow_get_all_info(name, user_id, db):
    function = available_functions[name]
    response = {
        "message": "Aqui está uma lista detalhada de todas suas informações salvas:",
        "infos": function(user_id, db),
    }

    return response


def flow_remove_info(tool_call_id, name, user_id, db):
    infos = get_all_info(user_id, db)

    info_str = ", ".join(info.model_dump_json() for info in infos)

    messages.append(
        {
            "content": "Encontre nessa lista de jsons a informação que é mais parecida com o que o usuário pediu para remover:"
            + info_str
            + ". Após encontrar, mostre a informação e pergunte se ele realmente quer remover",
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
        }
    )

    completion = client.chat.completions.create(model=LLMODEL, messages=messages)
    print("\nline 170:", completion.choices[0].message.content)
    return completion.choices[0].message.content
    # function = available_functions[name]
    # response = {
    #     "message": "Aqui está a função que você deseja apagar:",
    #     "infos": function(user_id, db),
    # }

    return response


def final_tool_message(content, tool_call_id, name):
    messages.append(
        {
            "content": content,
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
        }
    )

    completion = client.chat.completions.create(model=LLMODEL, messages=messages)
    return completion.choices[0].message.content
