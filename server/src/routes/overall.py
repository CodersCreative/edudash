from flask import jsonify, request
from sqlalchemy import select
from model_database import db, User, Reward, Punishment
from utils import get_user_by_id_or_email
from app import app


@app.route("/overall/leaderboard", methods=["GET"])
def get_overall_leaderboard():
    users = db.session.scalars(select(User).order_by(User.points.desc())).all()
    leaderboard = []
    for rank, user in enumerate(users, start=1):
        leaderboard.append(
            {"rank": rank, "username": user.username, "points": user.points}
        )
    return jsonify({"leaderboard": leaderboard}), 200


@app.route("/overall/points", methods=["GET"])
def get_overall_points():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"points": user.points}), 200


@app.route("/overall/history", methods=["GET"])
def get_overall_history():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    rewards = db.session.scalars(select(Reward).where(Reward.user_id == user.id)).all()

    punishments = db.session.scalars(
        select(Punishment).where(Punishment.user_id == user.id)
    ).all()

    history = []

    for reward in rewards:
        history.append(
            {
                "type": "reward",
                "id": reward.id,
                "points": reward.points,
                "reason": reward.reason,
                "activity_id": reward.activity_id,
                "teacher_id": reward.teacher_id,
            }
        )

    for punishment in punishments:
        history.append(
            {
                "type": "punishment",
                "id": punishment.id,
                "points": -punishment.points,
                "reason": punishment.reason,
                "teacher_id": punishment.teacher_id,
            }
        )

    return jsonify({"history": history}), 200
