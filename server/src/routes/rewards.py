from flask import jsonify, request
from sqlalchemy import select, func
from model_database import db, User, Reward
from app import app


@app.route("/reward/leaderboard", methods=["GET"])
def get_reward_leaderboard():
    users = db.session.scalars(select(User)).all()
    leaderboard = []

    for user in users:
        points = (
            db.session.scalar(
                select(func.sum(Reward.points)).where(Reward.user_id == user.id)
            )
            or 0
        )

        if points > 0:
            leaderboard.append({"username": user.username, "points": points})

    leaderboard.sort(key=lambda x: x["points"], reverse=True)

    for rank, entry in enumerate(leaderboard, start=1):
        entry["rank"] = rank

    return jsonify({"leaderboard": leaderboard}), 200


@app.route("/reward/points", methods=["GET"])
def get_reward_points():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    points = (
        db.session.scalar(
            select(func.sum(Reward.points)).where(Reward.user_id == user.id)
        )
        or 0
    )

    return jsonify({"points": points}), 200


@app.route("/rewards/history", methods=["GET"])
def get_rewards_history():
    data = request.get_json()
    user = get_user_by_id_or_email(data.get("user_id"), data.get("email"))

    if not user:
        return jsonify({"message": "User not found"}), 404

    rewards = db.session.scalars(select(Reward).where(Reward.user_id == user.id)).all()

    history = []
    for reward in rewards:
        history.append(
            {
                "id": reward.id,
                "points": reward.points,
                "reason": reward.reason,
                "activity_id": reward.activity_id,
                "teacher_id": reward.teacher_id,
            }
        )

    return jsonify({"history": history}), 200


@app.route("/reward", methods=["POST"])
def reward():
    data = request.get_json()
    user_id: int = data.get("user_id")
    teacher_id: int = data.get("teacher_id")
    activity_id: int | None = data.get("activity_id")
    reason = data.get("reason")
    points: int = data.get("points")
    user = db.session.scalar(select(User).where(User.id == user_id))
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.points += points
    reward = Reward(
        user_id=user_id,
        teacher_id=teacher_id,
        activity_id=activity_id,
        reason=reason,
        points=points,
    )
    db.session.add(reward)
    db.session.commit()
    return jsonify({"message": "Reward created successfully"}), 201
