from flask import jsonify, request

from .common.render import get_response_html


def controller(session_handler):
    data = request.get_json()

    session = data.get('session')
    branch = data.get('branch')
    
    conversation_history = session_handler.get_conversation_history(branch, session)
    if 'messages' in conversation_history:
        for message in conversation_history['messages']:
            if message['role'] == 'system':
                message['content'] = get_response_html(message['content'])
            else:
                message['content'] = message['content']

    return jsonify(conversation_history)