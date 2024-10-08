
#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    response = [hero.to_dict(only=("id", "name", "super_name")) for hero in heroes]
    return make_response(jsonify(response), 200)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = db.session.get(Hero, id)
    if not hero:
        error_body = {"error": "Hero not found"}
        return make_response(jsonify(error_body), 404)
    return make_response(jsonify(hero.to_dict()), 200)

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    response = [power.to_dict(only=('id', 'name', 'description')) for power in powers]
    return make_response(jsonify(response), 200)

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_detail(id):
    power = db.session.get(Power, id)
    if not power:
        error_body = {"error": "Power not found"}
        return make_response(jsonify(error_body), 404)

    if request.method == 'GET':
        return make_response(jsonify(power.to_dict(only=('id', 'name', 'description'))), 200)
    elif request.method == 'PATCH':
        data = request.get_json()
        description = data.get('description')
        if not description or len(description) < 20:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        power.description = description
        db.session.commit()
        return make_response(jsonify(power.to_dict(only=('id', 'name', 'description'))), 200)

@app.route('/hero_powers', methods=['GET', 'POST'])
def hero_powers():
    if request.method == 'GET':
        hero_powers = HeroPower.query.all()
        response = [hero_power.to_dict() for hero_power in hero_powers]
        return make_response(jsonify(response), 200)
    elif request.method == 'POST':
        data = request.get_json()
        strength = data.get('strength')
        power_id = data.get('power_id')
        hero_id = data.get('hero_id')

        valid_strengths = {'Strong', 'Weak', 'Average'}
        if strength not in valid_strengths:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        hero = db.session.get(Hero, hero_id)
        if not hero:
            return make_response(jsonify({"errors": ["Hero not found"]}), 404)
        power = db.session.get(Power, power_id)
        if not power:
            return make_response(jsonify({"errors": ["Power not found"]}), 404)

        existing_hero_power = HeroPower.query.filter_by(hero_id=hero_id, power_id=power_id).first()
        if existing_hero_power:
            return make_response(jsonify({"errors": ["This hero already has this power."]}), 400)

        new_hero_power = HeroPower(
            strength=strength,
            power_id=power_id,
            hero_id=hero_id
        )
        db.session.add(new_hero_power)
        db.session.commit()

        return make_response(jsonify(new_hero_power.to_dict()), 200)
if __name__ == '__main__':
    app.run(port=5555, debug=True)
