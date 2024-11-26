"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Favorite
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

app.config["JWT_SECRET_KEY"] = "LlaveSuperSecreta"  # Change this!
jwt = JWTManager(app)

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
    users = User.query.all()
    return jsonify([user.serialize() for user in users],), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'Error':'User not found'}), 404
    return jsonify(user.serialize()), 200

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).one_or_none()

    favorites = Favorite.query.filter_by(user_id=user.id).all()

    if favorites == []:
        return jsonify({"msg":"There are no favorites"}), 404
    return jsonify([favorite.serialize() for favorite in favorites],), 200

@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    return jsonify([people.serialize() for people in all_people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({'Error':'Person not found'}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'Error':'Planet not found'}), 404
    return jsonify(planet.serialize()), 200

#Esta ruta no va asi, se le pasa el user_id en body y se toma el request. lo dejo a modo de ejemplo de lo que NO hay que hacer
"""@app.route('/user/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(user_id, planet_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'Error':'User with id {user_id} not found'}), 404
    
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'Error':'Planet with id {planet_id} not found'}), 404
    
    new_favorite = Favorite(
        user_id = user_id,
        planet_id = planet_id
        )
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201
"""
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
@jwt_required()
def add_fav_planet(planet_id):

    email = get_jwt_identity()
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg" : "User doesn't exist"}), 404
    
    planet = Planet.query.get(planet_id)
    if planet == None:
        return jsonify({"msg" : "Planet doesn't exist"}), 404
    
    new_favorite = Favorite(
        user_id = user.id,
        planet_id = planet_id
        )
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_fav_planet(planet_id):
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg" : "User doesn't exist"}), 404
    
    planet = Planet.query.get(planet_id)
    if planet == None:
        return jsonify({"msg" : "Planet doesn't exist"}), 404
    
    favorite_delete = Favorite.query.filter_by(user_id=user.id,planet_id=planet.id).first()
    if favorite_delete == None:
        return jsonify({"msg" : "Favorite doesn't exist"}), 404
    db.session.delete(favorite_delete)
    db.session.commit()

    return jsonify({"msg" : "Favorite successfully deleted"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
@jwt_required()
def add_fav_people(people_id):
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg" : "User doesn't exist"}), 404
    
    people = People.query.get(people_id)
    if people == None:
        return jsonify({"msg" : "People doesn't exist"}), 404
    
    new_favorite = Favorite(
        user_id = user.id,
        people_id = people_id
        )
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
@jwt_required()
def delete_fav_people(people_id):
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg" : "User doesn't exist"}), 404
    
    people = People.query.get(people_id)
    if people == None:
        return jsonify({"msg" : "People doesn't exist"}), 404
    
    favorite_delete = Favorite.query.filter_by(user_id=user.id,people_id=people.id).first()
    if favorite_delete == None:
        return jsonify({"msg" : "Favorite doesn't exist"}), 404
    db.session.delete(favorite_delete)
    db.session.commit()

    return jsonify({"msg" : "Favorite successfully deleted"}), 201

@app.route("/login", methods=["POST"])

def login():
    body = request.json
    email = body.get("email", None)
    password = body.get("password", None)

    user = User.query.filter_by(email=email).one_or_none()

    if user == None:
        return jsonify({"msg": "Bad email or password"}), 401

    if user.password != password:
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 201

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
