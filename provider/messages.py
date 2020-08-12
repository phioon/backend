def get_message(lang_id, context, msg_id):
    if lang_id in messages and context in messages[lang_id] and msg_id in messages[lang_id][context]:
        return messages[lang_id][context][msg_id]
    else:
        return messages['enUS'][context][msg_id]


messages = {
    'enUS': {
        'generic': {
            'invalid_api_key': "Please, check your API KEY. Seems like it's not correctly set."
        },
        'eodlist': {
            'invalid_limit': "Please, check the parameter LIMIT. I couldn't convert it to an integer."
        }
    },
    'ptBR': {
        'generic': {
            'invalid_api_key': "Dê uma olhada na sua API KEY. Parece que ela não está corretamente configurada."
        },
        'eodlist': {
            'invalid_limit': "Dê uma olhada no parâmetro LIMIT. Não consegui converte-lo para o tipo inteiro."
        }
    }
}
