#!/usr/bin/env python3

from flask import Flask, request, make_response, send_from_directory, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False


migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
     return '<h1>Code Challenge</h1>'

class HeroesResource(Resource):
    def get(self, id=None):
        if id is None:
            heroes = Hero.query.all()
            return jsonify([hero.to_dict() for hero in heroes])
        else:
            hero = Hero.query.get(id)
            if hero:
                return jsonify(hero.to_dict(serialize_only=('id', 'name', 'super_name', 'hero_powers')))
            return jsonify({'error': 'Hero not found'}), 404

    def post(self):
        data = request.get_json()
        name = data.get('name')
        super_name = data.get('super_name')

        if not name or not super_name:
            return jsonify({'error': 'Name and Super Name are required'}), 400
        
        new_hero = Hero(name=name, super_name=super_name)
        db.session.add(new_hero)
        db.session.commit()
        return jsonify(new_hero.to_dict()), 201

class PowerResource(Resource):
    def get(self, id=None):
        if id is None:
            powers = Power.query.all()
            return jsonify([power.to_dict() for power in powers])
        else:
            power = Power.query.get(id)
            if power:
                return jsonify(power.to_dict())
            return jsonify({'error': 'Power not found'}), 404

    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')

        if not name or not description:
            return jsonify({'error': 'Name and Description are required'}), 400
        
        new_power = Power(name=name, description=description)
        db.session.add(new_power)
        db.session.commit()
        return jsonify(new_power.to_dict()), 201

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return jsonify({'error': 'Power not found'}), 404
        
        data = request.get_json()
        description = data.get('description')
        
        if description:
            try:
                power.description = description
                db.session.commit()
                return jsonify(power.to_dict())
            except ValueError as e:
                return jsonify({'errors': [str(e)]}), 400
            
        return {"errors": ["validation errors"]}, 400

class HeroPowerResource(Resource):
    def get(self):
        hero_powers = HeroPower.query.all()
        return jsonify([hero_power.to_dict() for hero_power in hero_powers])
    
    def post(self):
        data = request.get_json()
        strength = data.get('strength')
        power_id = data.get('power_id')
        hero_id = data.get('hero_id')
        
        if not strength or not power_id or not hero_id:
            return jsonify({'error': 'Strength, Power ID, and Hero ID are required'}), 400

        new_hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)
        db.session.add(new_hero_power)
        db.session.commit()
        return jsonify(new_hero_power.to_dict()), 201
        
api.add_resource(HeroesResource, '/heroes', '/heroes/<int:id>')
api.add_resource(PowerResource, '/powers', '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
