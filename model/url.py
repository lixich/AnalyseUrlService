from flask import Blueprint, jsonify, abort, request, make_response
from flask_sqlalchemy import SQLAlchemy, inspect
import count_tags
import json

app_url = Blueprint('', __name__)
db = SQLAlchemy()

class Url(db.Model):
    __tablename__ = 'Url'
    Id = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    Value = db.Column(db.String, nullable=False)
    Tags = db.Column(db.String, nullable=False)
    IsDone = db.Column(db.Boolean, nullable=False)
    IsValid = db.Column(db.Boolean)
    def __repr__(self):
        return f"<{self.Value}: {self.Tags}>"
    def __init__(self, value, tags, is_done, is_valid):
        self.Value = value
        self.Tags = tags
        self.IsDone = is_done
        self.IsValid = is_valid
    def serialize(self):
        url = {c: getattr(self, c) for c in inspect(self).attrs.keys()}
        if url['Tags']:
            for key, value in dict(json.loads(url['Tags'])).items():
                url[key] = value
        del url['Tags']
        return url

@app_url.route('/<int:url_id>', methods = ['GET'])
def get_url(url_id):
    url = Url.query.filter_by(Id=url_id).first()
    if not url:
        abort(404)
    return jsonify(dict(url.serialize()))

@app_url.route('/', methods = ['POST'])
def create_url():
    if not request.json:
        abort(400)
    tags_dict = count_tags.get(request.json['Value'])
    tags = str(json.dumps(tags_dict)) if tags_dict else ''
    is_valid = bool(tags)
    url = Url(request.json['Value'], tags, True, is_valid)
    db.session.add(url)
    db.session.commit()
    return jsonify(dict(url.serialize()))

@app_url.route('/<int:url_id>', methods=['PUT'])
def update_url(url_id):
    url = Url.query.filter_by(Id=url_id).first()
    if not url:
        abort(404)
    if not request.json:
        abort(400)
    url.Value = request.json['Value']
    url.IsDone = request.json['IsDone']
    url.IsValid = request.json['IsValid']
    tags = {}
    tags_key = set(dict(request.json).keys()) - (set(inspect(url).attrs.keys()))
    for tag_key in tags_key:
        tags[tag_key] = request.json[tag_key]
    url.Tags = str(json.dumps(tags))
    db.session.commit()
    return jsonify(dict(url.serialize()))

@app_url.route('/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    url = Url.query.filter_by(Id=url_id).first()
    if url:
        Url.query.filter_by(Id=url_id).delete()
        return jsonify({'Result': True})
    else:
        abort(404)
