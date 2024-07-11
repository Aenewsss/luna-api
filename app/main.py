import json
import logging
import os
import sys
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from groq import Groq
from requests import Session
import requests
from app.info.info import get_all_info, remove_info, save_info, update_info
from app.models import models
from app.classes.classes import InfoCreate, MessageRequest, User
from app.environments import (
    GRAPH_API_TOKEN,
    LLMODEL,
    LUNA_DEV_KEY,
    WEBHOOK_WPP_VERIFY_TOKEN,
)
from app.constants.messages import messages
from app.constants.tools import tools
from app.constants.available_functions import available_functions
from app.auth.auth import router as auth_router, validate_token
from app.database.database import engine, get_db
from app.middlewares.user import UserMiddleware
from app.models.models import User as UserModel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Luna API", root_path="/api")

app.include_router(auth_router, prefix="/auth")

client = Groq(api_key=LUNA_DEV_KEY)

# create tables if doesn't exist yet
models.Base.metadata.create_all(bind=engine)

# app.add_middleware(UserMiddleware)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.get("/")
async def hello_world():
    print("\nline 207\n")
    return {"message": "Hello World!"}

@app.post("/scheduleappointment")
async def schedule_appointment(request: Request):
    try:
        data = await request.json()
        print("Received data:", data)
        # Handle the data here
        # Return a response with a status code 200
        return Response(status_code=200)
    except Exception as e:
        print("Error:", e)
        return Response(status_code=500, content={"message": "Internal Server Error"})

@app.get("/wpp-webhook")
async def wpp_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print(
        "\nmode, token, challenge, verify_token",
        mode,
        token,
        challenge,
        WEBHOOK_WPP_VERIFY_TOKEN,
    )

    if mode == "subscribe" and token == WEBHOOK_WPP_VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    else:
        return JSONResponse(content={"error": "Forbidden"}, status_code=403)


@app.post("/wpp-webhook")
async def chat_wpp(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()

        if not data.get("entry"):
            raise HTTPException(status_code=200, detail="Invalid data")

        entry = data["entry"][0]
        if not entry.get("changes"):
            raise HTTPException(status_code=200, detail="Invalid data")

        changes = entry["changes"][0]
        value = changes.get("value")
        if not value:
            raise HTTPException(status_code=200, detail="Invalid data")

        messages = value.get("messages")
        if not messages:
            raise HTTPException(status_code=200, detail="Invalid data")

        message = messages[0]

        print('\nline 102 data', data, '\n')

        if message.get("type") == "text":
            business_phone_number_id = value.get("metadata", {}).get("phone_number_id")
            if not business_phone_number_id:
                raise HTTPException(status_code=200, detail="Invalid data")

            user_phone = message.get("from")
            user_message = message.get("text", {}).get("body")

            if user_phone:
                user = db.query(UserModel).filter(UserModel.phone == user_phone).first()

                if not user:
                    raise HTTPException(status_code=404, detail="User not found")

                user_id = user.id
                user_name = user.name

            response_data = await chatLuna(db, user_message, user_id, user_name)

            print('\nline 120 response_data',response_data, '\n')
            # Send a WhatsApp message
            requests.post(
                f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {GRAPH_API_TOKEN}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": user_phone,
                    "text": {"body": response_data["text"]},
                    # "context": {"message_id": message["id"]},  # Uncomment if you want to reply user message
                },
            )

            if response_data["template"]:
                # Send a WhatsApp message
                response_data["template"]["to"] = user_phone

                print('\nline 124 response_data:',response_data["template"],'\n')
                requests.post(
                    f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                    headers={"Authorization": f"Bearer {GRAPH_API_TOKEN}"},
                    json=response_data["template"],
                )

            # Mark the message as read
            requests.post(
                f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {GRAPH_API_TOKEN}"},
                json={
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message["id"],
                },
            )
        elif message.get("type") == "button":
            business_phone_number_id = value.get("metadata", {}).get("phone_number_id")
            
            user_phone = message.get("from")

            button_payload = message.get("button", {}).get("payload")
            button_text = message.get("button", {}).get("text")

            if button_text == "Sim":
                if 'remove' in button_payload:
                    length = len(button_payload)
                    id = button_payload[length - 1:length + 1]
                    response_text = remove_info(id, db)['text']
                elif 'update' in button_payload:
                    print('\nbutton_payload_update', button_payload)

                    index_id = button_payload.find('id:')
                    id = button_payload[index_id + 3:index_id + 4]

                    print('\nline 174 id:', id)

                    index_content = button_payload.find('content:')
                    content = button_payload[index_content + 8:index_content + len(button_payload) -1]
                    print('\nline 180 id:', content)

                    response_text = update_info(id, content, db)['text']
            elif button_text == "Não":
                response_text = "Solicitação cancelada."

            # Send a response based on the button clicked
            requests.post(
                f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {GRAPH_API_TOKEN}"},
                json={
                    "messaging_product": "whatsapp",
                    "to": user_phone,
                    "text": {"body": response_text},
                    "context": {"message_id": message["id"]},  # Uncomment if you want to reply user message
                },
            )

            # Mark the message as read
            requests.post(
                f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {GRAPH_API_TOKEN}"},
                json={
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message["id"],
                },
            )

        return Response(status_code=200)

    except HTTPException as e:
        logger.error(f"HTTP error 141: {e}", exc_info=True)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Unhandled error 143: {e}", exc_info=True)
        return Response(status_code=200)


async def chatLuna(db, user_message, user_id, user_name):
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
        print("message:", completion.choices[0].message.content)
        return {"text": completion.choices[0].message.content}
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
                return flow_remove_info(tool_call_id=tool_call.id, name=name, user_id=user_id, db=db)
            elif name == "update_info":
                return flow_update_info(tool_call_id=tool_call.id, name=name, user_id=user_id, db=db) 

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
    response = (
        "Aqui está uma lista detalhada de todas suas informações salvas:"
        + "".join(map(str, function(user_id, db)))
    )

    return {"text": response}

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

    llama_response = completion.choices[0].message.content

    messages.append(
        {
            "content": "Baseado nessa resposta que você me forneceu:"
            + llama_response
            + "Encontre o id da informação na seguinte lista:"
            + info_str
            + " e retorne somente o id no seguinte formato: '{'id': '[id encontrado]'}'"
            ,
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
        }
    )

    completion_info_id = client.chat.completions.create(model=LLMODEL, messages=messages)

    info_id = completion_info_id.choices[0].message.content

    print('\nline 365:', info_id)

    template_message = {
        "messaging_product": "whatsapp",
        # "to": user_phone,
        "type": "template",
        "template": {
            "name": "remove_info",
            "language": {
                "code": "pt_BR"
            },
             "components": [
            {
                "type": "button",
                "sub_type": "quick_reply",
                "index": "0",
                "parameters": [
                    {
                        "type": "payload",
                        "payload": "keep_info"
                    }
                ]
            },
            {
                "type": "button",
                "sub_type": "quick_reply",
                "index": "1",
                "parameters": [
                    {
                        "type": "payload",
                        "payload": f"remove_info:{2}"
                    }
                ]
            }
        ]
        }
    }

    return {"text": llama_response, "template": template_message}

def flow_update_info(tool_call_id, name, user_id, db):
    infos = get_all_info(user_id, db)

    info_str = ", ".join(info.model_dump_json() for info in infos)

    messages.append(
        {
            "content": "Encontre nessa lista de jsons a informação que é mais parecida com o que o usuário pediu para editar/atualizar/alterar:"
            + info_str
            + ". Após encontrar, mostre a informação e pergunte se ele realmente quer trocar pela informação que ele mandou",
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
        }
    )

    completion = client.chat.completions.create(model=LLMODEL, messages=messages)

    llama_response = completion.choices[0].message.content

    messages.append(
        {
            "content": "Baseado nessa resposta que você me forneceu:"
            + llama_response
            + "Encontre o id da informação na seguinte lista:"
            + info_str
            + " e retorne somente o id no seguinte formato: {id=[id encontrado]}"
            ,
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
        }
    )

    completion_info_id = client.chat.completions.create(model=LLMODEL, messages=messages)

    info_id_str = completion_info_id.choices[0].message.content

    print('\nline 441:', info_id_str)
    index =  info_id_str.find('id')
    print('\nline 442:', info_id_str[index + 3 : len(info_id_str) - 1])

    info_id = info_id_str[index + 3 : len(info_id_str) - 1]

    messages.append(
        {
            "content": "Baseado nessa resposta que você me forneceu:"
            + llama_response
            + "Encontre somente o novo conteúdo que será alterado e retorne-o no seguinte formato: {content=[novo content]}",
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
        }
    )

    completion_info_content = client.chat.completions.create(model=LLMODEL, messages=messages)

    info_content_str = completion_info_content.choices[0].message.content

    print('\nline 468:', info_content_str)
    index_content =  info_content_str.find('content')
    print('\nline 470:', info_content_str[index_content + 8 : len(info_content_str) -1])

    info_content = info_content_str[index_content + 8 : len(info_content_str) -1].replace('"', '')

    template_message = {
        "messaging_product": "whatsapp",
        # "to": user_phone,
        "type": "template",
        "template": {
            "name": "update_info",
            "language": {
                "code": "pt_BR"
            },
             "components": [
            {
                "type": "button",
                "sub_type": "quick_reply",
                "index": "0",
                "parameters": [
                    {
                        "type": "payload",
                        "payload": "keep_info"
                    }
                ]
            },
            {
                "type": "button",
                "sub_type": "quick_reply",
                "index": "1",
                "parameters": [
                    {
                        "type": "payload",
                        "payload": f"update_info_id:{info_id}_update_info_content:{info_content}"
                    }
                ]
            }
        ]
        }
    }

    return {"text": llama_response, "template": template_message}

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
    return {"text": completion.choices[0].message.content}
