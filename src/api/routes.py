from flask import Blueprint, request, jsonify
from api.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash



api = Blueprint('api', __name__)

def register_api(app):
    app.register_blueprint(api, url_prefix='/api')







@api.route('/register', methods=['POST']) #sirve para verificar si el usuario existe y sino crear uno nuevo
def register():
    username = request.json['username']
    password = request.json['password']

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"msg": "Username already taken"}), 400

    hashed_password = generate_password_hash(password)

    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201





@api.route('/login', methods=['POST']) #da error en postman,  
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()  # inicio de sesion
 
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Invalid username or password"}), 401




@api.route("/token", methods=["POST"])    #crear token
def create_token():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token, "user_id": user.id})


@api.route("/judit", methods=["GET"]) #esta es la pagina protegina
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200







