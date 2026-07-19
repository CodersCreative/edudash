from flask import jsonify, request
from model_database import CULTURAL_TYPE
from utils import (
    get_points_by_activity_type,
    get_leaderboard_by_activity_type,
    get_user_by_id_or_email,
)
from app import app


@app.route("/cultural/leaderboard", methods=["GET"])
def get_cultural_leaderboard():
    leaderboard = get_leaderboard_by_activity_type(CULTURAL_TYPE)
    return jsonify({"leaderboard": leaderboard}), 200


@app.route("/cultural/points", methods=["GET"])
def get_cultural_points():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role >= 3:
        return jsonify({"points": 0}), 200

    points = get_points_by_activity_type(user.id, CULTURAL_TYPE)
    return jsonify({"points": points}), 200
