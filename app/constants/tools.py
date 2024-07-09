tools = [
    {
        "type": "function",
        "function": {
            "name": "save_info",
            "description": "Salvar informações solicitadas pelo usuário",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "message": "Mensagem padrão após salvar informação",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_info",
            "description": "Listar todas as informações do usuário",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "message": "Mensagem padrão após salvar informação",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_info",
            "description": "Remover uma informação específica do usuário",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "message": "Mensagem padrão após salvar informação",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_info",
            "description": "Atualizar, editar ou alterar uma informação específica do usuário",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "message": "Mensagem padrão após salvar informação",
                    }
                },
            },
        },
    },
]
