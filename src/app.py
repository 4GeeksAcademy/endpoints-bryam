"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, abort
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from sqlalchemy import select
from models import db, Users, Pokemons, Habilidades, Trainers, Favourites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = db.session.execute(select(Users)).scalars().all()
    return jsonify([u.serialize() for u in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # simple validation
    if not data or not all(k in data for k in ("email","password","username")):
        return jsonify({"error": "Missing data"}), 400
    new_user = Users(
        email=data['email'],
        password=data['password'],
        username=data['username'],
        firstname=data.get('firstname'),
        lastname=data.get('lastname')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

# Pokemons endpoints
@app.route('/pokemons', methods=['GET'])
def get_pokemons():
    pokes = db.session.execute(select(Pokemons)).scalars().all()
    return jsonify([p.serialize() for p in pokes]), 200

@app.route('/pokemons/<int:poke_id>', methods=['GET'])
def get_pokemon(poke_id):
    poke = db.session.get(Pokemons, poke_id)
    if not poke:
        return jsonify({"error": "Pokemon not found"}), 404
    return jsonify(poke.serialize()), 200

@app.route('/pokemons', methods=['POST'])
def create_pokemon():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing data"}), 400
    new_poke = Pokemons(
        name=data['name'],
        pokemon_type=data.get('pokemon_type'),
        is_legendary=data.get('is_legendary', False)
    )
    db.session.add(new_poke)
    db.session.commit()
    return jsonify(new_poke.serialize()), 201

@app.route('/habilidades', methods=['GET'])
def get_habilidades():
    habs = db.session.execute(select(Habilidades)).scalars().all()
    return jsonify([h.serialize() for h in habs]), 200

@app.route('/habilidades/<int:hab_id>', methods=['GET'])
def get_habilidad(hab_id):
    hab = db.session.get(Habilidades, hab_id)
    if not hab:
        return jsonify({"error": "Habilidad not found"}), 404
    return jsonify(hab.serialize()), 200

@app.route('/trainers', methods=['GET'])
def get_trainers():
    trs = db.session.execute(select(Trainers)).scalars().all()
    return jsonify([t.serialize() for t in trs]), 200

@app.route('/trainers/<int:tr_id>', methods=['GET'])
def get_trainer(tr_id):
    tr = db.session.get(Trainers, tr_id)
    if not tr:
        return jsonify({"error": "Trainer not found"}), 404
    return jsonify(tr.serialize()), 200

@app.route('/favourites', methods=['GET'])
def get_favourites():
    favs = db.session.execute(select(Favourites)).scalars().all()
    return jsonify([f.serialize() for f in favs]), 200

@app.route('/favourites', methods=['POST'])
def add_favourite():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    fav = Favourites(
        user_id=user_id,
        pokemon_id=data.get('pokemon_id'),
        habilidad_id=data.get('habilidad_id'),
        trainer_id=data.get('trainer_id')
    )
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201

@app.route('/favourites', methods=['DELETE'])
def remove_favourite():
    data = request.get_json()
    stmt = select(Favourites).where(
        Favourites.user_id==data.get('user_id'),
        Favourites.pokemon_id==data.get('pokemon_id')
    )
    fav = db.session.execute(stmt).scalars().first()
    if not fav:
        return jsonify({"error": "Favourite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Removed"}), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
