# Schema JSON que define a estrutura de saída esperada da LLM
SCHEMA_SAIDA: dict = {
    "type": "json_schema",
    "json_schema": {
        "name": "RespostaEstruturada",
        "schema": {
            "type": "object",
            "properties": {
                "raciocinio":    {"type": "string", "description": "Passo a passo utilizado para se chegar à resposta"},
                "cliente":       {"type": "string", "description": "Contexto que o cliente trouxe"},
                "sua_resposta":  {"type": "string", "description": "A resposta final ao usuário"},
            },
            "required": ["raciocinio", "cliente", "sua_resposta"],
            "additionalProperties": False,
        },
    },
}
