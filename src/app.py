"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from api.routes import register_api
from api.utils import generate_sitemap, APIException  # Asegúrate de esta importación
from flask_cors import CORS
from flask_jwt_extended import JWTManager


app = Flask(__name__)
CORS(app)
static_file_dir = os.path.join(os.path.dirname(__file__), 'static')

app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config["JWT_SECRET_KEY"] = "secretAccess"
jwt = JWTManager(app)

register_api(app)



@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/admin')
def admin():
    return "Admin Page"



@app.route('/')
def sitemap():
    if app.config['ENV'] == "development":
        return generate_sitemap(app)
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response




if __name__ == '__main__':
    app.run(debug=True)
