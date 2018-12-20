from flask import jsonify

def create_message_error(error):
    return jsonify({
        'Status': error.code,
        'Message' : str(error.description)
    }), error.code
