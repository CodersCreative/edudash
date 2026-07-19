from flask import jsonify, request
from model_database import ACADEMIC_TYPE
from utils import (
    get_points_by_activity_type,
    get_leaderboard_by_activity_type,
    get_user_by_id_or_email,
)
from app import app


@app.route("/academic/leaderboard", methods=["GET"])
def get_academic_leaderboard():
    leaderboard = get_leaderboard_by_activity_type(ACADEMIC_TYPE)
    return jsonify({"leaderboard": leaderboard}), 200


@app.route("/academic/points", methods=["GET"])
def get_academic_points():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role >= 3:
        return jsonify({"points": 0}), 200

    points = get_points_by_activity_type(user.id, ACADEMIC_TYPE)
    return jsonify({"points": points}), 200
