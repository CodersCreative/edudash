from flask import json, request, jsonify, send_file
from sqlalchemy import select, func
from model_database import (
    ADMIN_ROLE,
    STUDENT_ROLE,
    TEACHER_ROLE,
    Activity,
    UserActivity,
    db,
    User,
)
import bcrypt
from utils import (
    get_project_path,
)
from app import app


def create_tables():
    with app.app_context():
        db.create_all()


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role: int | None = data.get("role")
    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    existing_user = db.session.scalar(select(User).where(User.email == email))
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    if role is None:
        count = db.session.scalar(select(func.count()).select_from(User)) or 0
        if count > 0:
            role = STUDENT_ROLE
        else:
            role = ADMIN_ROLE

    user = User(username=username, email=email, password=password, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
            "message": "Registration successful",
            "username": user.username,
            "id": user.id,
            "role": user.role,
            "points": user.points,
        }
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password: str = data.get("password")

    user = db.session.scalar(select(User).where(User.email == email))

    if user and bcrypt.checkpw(password.encode(), user.password):
        return jsonify(
            {
                "message": "Login successful",
                "username": user.username,
                "id": user.id,
                "role": user.role,
                "points": user.points,
            }
        )
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/profile/picture", methods=["POST"])
def set_profile_picture():
    id = json.load(request.files["json"])["user_id"]
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Filename required"}), 401

    name = f"{get_project_path()}/src/profiles/{id}_{f.filename}"
    f.save(name)
    user = db.session.scalar(select(User).where(User.id == id))

    if not user:
        return jsonify({"message": "User not found"}), 404

    user.profile_picture = name
    db.session.commit()

    return jsonify({"message": "Points updated"}), 200


@app.route("/profile/picture", methods=["GET"])
def get_profile_picture():
    data = request.get_json()
    id = data.get("id")
    user = db.session.scalar(select(User).where(User.id == id))

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.profile_picture:
        return send_file(user.profile_picture), 200
    else:
        return jsonify({"message": "User has no image"}), 401


@app.route("/users", methods=["GET"])
def get_all_users():
    users = db.session.scalars(select(User)).all()
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
        for user in users
    ]
    return jsonify({"users": user_list}), 200


@app.route("/users/students", methods=["GET"])
def get_all_students():
    users = db.session.scalars(select(User)).all()
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
        for user in users
        if user.role < TEACHER_ROLE
    ]
    return jsonify({"users": user_list}), 200


import routes.academics
import routes.cultural
import routes.overall
import routes.punishments
import routes.rewards
import routes.sports
import routes.library
import routes.activity

if __name__ == "__main__":
    create_tables()
    app.run(port=5000, debug=True)
