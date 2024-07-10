"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from api.utils import APIException, generate_sitemap
from api.models import db
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
# from flask_login import LoginManager, login_user, logout_user, login_required
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
# from src.api.models  import User 


# from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix


# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file


@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response


@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('auth/login.html')
        else:
            flash("User not found...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    




@api.route("/user/exist", methods=["POST"])
def user_exist():
    email =request.json.get("email",None)
    password = request.json.get ("password", None)

    user = User.query.filter_by (email = email).first()
    print(user)

    if user is None:
        return jsonify ({
            "msg" : "email is not correct"
        }), 404
    
    if password != user.password:
        return jsonify ({
            "msg" : "password is not correct"
        }), 404
    
    access_token = create_access_token (identity = email)
    return jsonify (access_token = access_token)




@api.route ("/singup", methods = ["POST"])
def singup():
    body =request.get.json()
    print(body)
    user = User.query.filter_by (email = body ["email"]).first()
    print (user)
    if user is None:
        user =User(email =body["email"], password = body ["password"], is_active =True)
        db.sessionadd(user)
        db.session.commit()
        response_body = {
            "msg" : "usesr created"
        }
        return jsonify (response_body), 200
    else:
        return jsonify ({
            "msg":"this user has already been created"
        })










@app.route("/token", methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token, "user_id": user.id})


@app.route("/judit", methods= ["GET"])
@jwt_required()
def protected():
    current_user =get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('home'))
# @app.route('/protected')
# @login_required
# def protected():
#     return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"
app.register_blueprint(api, url_prefix='/api')
app.config["JWT_SECRET_KEY"] = "secretAccess" 
jwt = JWTManager(app)
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
