from flask import jsonify, request
from sqlalchemy import select, func
from model_database import db, User, Punishment
from utils import get_user_by_id_or_email
from app import app


@app.route("/punish/leaderboard", methods=["GET"])
def get_punish_leaderboard():
    users = db.session.scalars(select(User)).all()
    leaderboard = []

    for user in users:
        points = (
            db.session.scalar(
                select(func.sum(Punishment.points)).where(Punishment.user_id == user.id)
            )
            or 0
        )

        if points > 0:
            leaderboard.append({"username": user.username, "points": points})

    leaderboard.sort(key=lambda x: x["points"], reverse=True)

    for rank, entry in enumerate(leaderboard, start=1):
        entry["rank"] = rank

    return jsonify({"leaderboard": leaderboard}), 200


@app.route("/punish/points", methods=["GET"])
def get_punish_points():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    points = (
        db.session.scalar(
            select(func.sum(Punishment.points)).where(Punishment.user_id == user.id)
        )
        or 0
    )

    return jsonify({"points": points}), 200


@app.route("/punish/history", methods=["GET"])
def get_punishments_history():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    punishments = db.session.scalars(
        select(Punishment).where(Punishment.user_id == user.id)
    ).all()

    history = []
    for punishment in punishments:
        history.append(
            {
                "id": punishment.id,
                "points": punishment.points,
                "reason": punishment.reason,
                "teacher_id": punishment.teacher_id,
            }
        )

    return jsonify({"history": history}), 200


@app.route("/punish", methods=["POST"])
def punish():
    data = request.get_json()
    user_id: int = data.get("user_id")
    teacher_id: int = data.get("teacher_id")
    reason = data.get("reason")
    points: int = data.get("points")
    user = db.session.scalar(select(User).where(User.id == user_id))

    if not user:
        return jsonify({"message": "User not found"}), 404

    user.points -= points
    punishment = Punishment(
        user_id=user_id, teacher_id=teacher_id, reason=reason, points=points
    )
    db.session.add(punishment)
    db.session.commit()
    return jsonify({"message": "Punishment created successfully"}), 201
