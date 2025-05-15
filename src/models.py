from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List


db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(30), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(80), nullable=True)
    lastname: Mapped[str] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    favourite: Mapped[List["Favourites"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "created_at": self.created_at.isoformat(),
            "favourites": [fav.serialize() for fav in self.favourite]
        }

            # do not serialize the password, its a security breach
    
class Pokemons(db.Model):
    __tablename__ = "pokemons"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    pokemon_type: Mapped[str] = mapped_column(String(50), nullable=True)
    is_legendary: Mapped[bool] = mapped_column(Boolean(), default=False)

    favourite: Mapped[List["Favourites"]] = relationship(back_populates="pokemon")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "pokemon_type": self.pokemon_type,
            "is_legendary": self.is_legendary,
            "favourited_by": [fav.user.username for fav in self.favourite]
        }

class Habilidades(db.Model):
    __tablename__ = "habilidades"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    power: Mapped[int] = mapped_column(Integer, nullable=True)
    accuracy: Mapped[int] = mapped_column(Integer, nullable=True)

    favourite: Mapped[List["Favourites"]] = relationship(back_populates="habilidad")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "power": self.power,
            "accuracy": self.accuracy,
            "favourited_by": [fav.user.username for fav in self.favourite]
        }

class Trainers(db.Model):
    __tablename__ = "trainers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    hometown: Mapped[str] = mapped_column(String(80), nullable=True)

    favourite: Mapped[List["Favourites"]] = relationship(back_populates="trainer")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "hometown": self.hometown,
            "favourited_by": [fav.user.username for fav in self.favourite]
        }

class Favourites(db.Model):
    __tablename__ = "favourites"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemons.id"), nullable=True)
    habilidad_id: Mapped[int] = mapped_column(ForeignKey("habilidades.id"), nullable=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"), nullable=True)

    user: Mapped[Users] = relationship(back_populates="favourite")
    pokemon: Mapped[Pokemons] = relationship(back_populates="favourite")
    habilidad: Mapped[Habilidades] = relationship(back_populates="favourite")
    trainer: Mapped[Trainers] = relationship(back_populates="favourite")

    def serialize(self):
        return {
            "user": self.user.username,
            "pokemon": self.pokemon.name if self.pokemon else None,
            "habilidad": self.habilidad.name if self.habilidad else None,
            "trainer": self.trainer.name if self.trainer else None
        }
