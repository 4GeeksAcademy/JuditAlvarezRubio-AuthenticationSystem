from flask import Blueprint, request, jsonify
from api.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
api = Blueprint('api', __name__)

def register_api(app):
    app.register_blueprint(api, url_prefix='/api')



@api.route('/admin')
def admin():
    return "Admin Page"


@api.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User(username=username, password=password)  # Cambiar para reflejar el modelo

    logged_user = User.login(db, user)  # Asegúrate de que este método esté implementado correctamente
    if logged_user:
        access_token = create_access_token(identity=logged_user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid username or password"}), 401

@api.route("/user/exist", methods=["POST"])
def user_exist():
    email = request.json.get("email")
    password = request.json.get("password")

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"msg": "Email is not correct"}), 404

    if password != user.password:
        return jsonify({"msg": "Password is not correct"}), 404

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)

@api.route("/signup", methods=["POST"])
def signup():
    body = request.get_json()
    user = User.query.filter_by(email=body["email"]).first()
    if user is None:
        user = User(email=body["email"], password=body["password"], is_active=True)
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User created"}), 200
    return jsonify({"msg": "This user has already been created"}), 409

@api.route("/token", methods=["POST"])
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

@api.route("/judit", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
