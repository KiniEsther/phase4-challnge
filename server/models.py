
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  
    super_name = db.Column(db.String(100))  


    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    def to_dict(self, only=None):
        """Convert Hero instance to dictionary representation."""
        data = {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name,
            "hero_powers": [hp.to_dict_minimal() for hp in self.hero_powers]
        }
        if only:
            return {key: data[key] for key in only if key in data}
        return data

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) 
    description = db.Column(db.String)  


    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')

    def to_dict(self, only=None):
        """Convert Power instance to dictionary representation."""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
        if only:
            return {key: data[key] for key in only if key in data}
        return data

    @validates('description')
    def validate_description(self, key, value):
        """Validate the length of the description."""
        if len(value) < 20:
            raise ValueError("description must be at least 20 characters long")
        return value

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)


    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    def to_dict(self, only=None):
        """Convert HeroPower instance to dictionary representation."""
        data = {
            "id": self.id,
            "strength": self.strength,
            "hero_id": self.hero_id,
            "power_id": self.power_id,
            "hero": self.hero.to_dict(),
            "power": self.power.to_dict(),
        }
        if only:
            return {key: data[key] for key in only if key in data}
        return data

    def to_dict_minimal(self):
        """Convert HeroPower instance to minimal dictionary representation."""
        return {
            "id": self.id,
            "strength": self.strength,
            "hero_id": self.hero_id,
            "power_id": self.power_id,
        }

    @validates('strength')
    def validate_strength(self, key, value):
        """Validate the strength field."""
        if value not in ['Strong', 'Weak', 'Average']:
            raise ValueError("strength must be one of: 'Strong', 'Weak', 'Average'")
        return value

    def __repr__(self):
        return f'<HeroPower {self.id}>'
