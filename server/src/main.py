import random
from flask import Flask, Response, json, request, jsonify, send_file
from model_database import CodingChallenges, CodingChallengesChecks, CodingChallengesStatements, db, User
from flask_cors import CORS
from typing import Optional
import bcrypt
import os

from utils import get_project_root

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_tables():
    with app.app_context():
        db.create_all()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    is_teacher : bool = data.get("is_teacher")
    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt());

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(username=username, email=email, password=password, is_teacher=is_teacher)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password : str = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.checkpw(password.encode(), user.password):
        return jsonify({"message": "Login successful", "username": user.username, "id" : user.id, "points": user.points})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/profile/picture", methods=["POST"])
def set_profile_picture():
    id = json.load(request.files["json"])["user_id"]
    f = request.files["file"];

    if not f.filename:
        return jsonify({"error": "Filename required"}), 401

    name = f"{get_project_root()}/src/profiles/{id}_{f.filename}";

    f.save(name)
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.profile_picture = name
    db.session.commit()

    return jsonify({'message': 'Points updated'}), 200

@app.route("/profile/picture", methods=["GET"])
def get_profile_picture():
    data = request.get_json()
    id = data.get("id")
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.profile_picture :
        return send_file(user.profile_picture), 200
    else:
        return jsonify({'message': 'User has no image'}), 401

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    users = User.query.order_by(User.points.desc()).all()
    leaderboard = []
    for rank, user in enumerate(users, start=1):
        leaderboard.append({
            'rank': rank,
            'username': user.username,
            'points': user.points
        })
    return jsonify({'leaderboard': leaderboard}), 200

@app.route('/points', methods=['POST'])
def update_points():
    data = request.get_json()
    return update_users_points(data.get('points'), data.get('id'), data.get('email'))

def get_username(id = None, email = None) -> Optional[str]:
    user = None;
    if email is None:
        user = User.query.filter_by(id=id).first()
    elif id is None:
        user = User.query.filter_by(email=email).first()

    if not user:
        return None

    return user.username

def update_users_points(new_points : int, id = None, email = None) -> tuple[Response, int]:
    user = None;
    if email is None:
        user = User.query.filter_by(id=id).first()
    elif id is None:
        user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404


    if new_points > user.points:
        user.points += new_points
        db.session.commit()

    return jsonify({'message': 'Points updated'}), 200

if __name__ == "__main__":
    create_tables()
    app.run(port=5000, debug=True)
