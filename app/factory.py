import os
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from db import db
from storage import init_minio
from auth import auth_bp
from files import files_bp
import models


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager(app)

    @login_manager.user_loader
    def _load_user(user_id):
        from models import Student
        return db.session.get(Student, int(user_id))

    @login_manager.unauthorized_handler
    def _unauthorized():
        return jsonify({"error": "Login required"}), 401

    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)

    with app.app_context():
        db.create_all()
        init_minio()

    return app
