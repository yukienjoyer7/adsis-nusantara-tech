from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from db import db
from models import Student

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    nim = data.get("nim", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not name or not nim or not password:
        return jsonify({"error": "name, nim, and password are required"}), 400

    student = Student(
        name=name,
        nim=nim,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(student)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "NIM already registered"}), 409

    login_user(student)
    return jsonify({"id": student.id, "name": student.name, "nim": student.nim, "email": student.email}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()
    nim = data.get("nim", "").strip()
    password = data.get("password", "")

    student = Student.query.filter_by(nim=nim).first()
    if student is None or not check_password_hash(student.password_hash, password):
        return jsonify({"error": "Invalid NIM or password"}), 401

    login_user(student)
    return jsonify({"id": student.id, "name": student.name, "nim": student.nim, "email": student.email})


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@auth_bp.get("/me")
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "nim": current_user.nim,
        "email": current_user.email,
    })
