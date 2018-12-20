import config
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import default_exceptions

app = Flask(__name__)
CORS(app, supports_credentials=True)

def register_blueprints():
    import errorhandler
    from model.url import app_url, db as db_url
    for code, ex in default_exceptions.items():
        app.errorhandler(code)(errorhandler.create_message_error)
    app.register_blueprint(app_url, url_prefix='/url')
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db_url.init_app(app)
    with app.app_context():
        db_url.create_all()

register_blueprints()

if __name__ == '__main__':
    app.run(host=config.HOST, debug = True, threaded=True)
