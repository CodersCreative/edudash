from flask import jsonify, request
from sqlalchemy import select
from model_database import STUDENT_ROLE, TEACHER_ROLE, db, User, Activity, UserActivity
from utils import get_user_by_id_or_email
from app import app


@app.route("/activity", methods=["POST"])
def create_activity():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    activity_type = data.get("type")
    teacher_id = data.get("teacher_id")

    if not name or activity_type is None:
        return jsonify({"message": "Name and type are required"}), 400

    teacher = get_user_by_id_or_email(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    activity = Activity(name=name, description=description, type=activity_type)
    db.session.add(activity)
    db.session.commit()

    user_activity = UserActivity(
        user_id=teacher.id, activity_id=activity.id, role=TEACHER_ROLE
    )

    db.session.add(user_activity)
    db.session.commit()

    return jsonify(
        {"message": "Activity created successfully", "activity_id": activity.id}
    ), 201


@app.route("/activity/<int:activity_id>/members", methods=["POST"])
def add_user_to_activity(activity_id):
    data = request.get_json()
    user_id = data.get("user_id")
    role = data.get("role", STUDENT_ROLE)

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    activity = db.session.scalar(select(Activity).where(Activity.id == activity_id))
    if not activity:
        return jsonify({"message": "Activity not found"}), 404

    user = get_user_by_id_or_email(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    existing = db.session.scalar(
        select(UserActivity).where(
            UserActivity.user_id == user_id, UserActivity.activity_id == activity_id
        )
    )
    if existing:
        return jsonify({"message": "User already in activity"}), 400

    user_activity = UserActivity(user_id=user.id, activity_id=activity_id, role=role)
    db.session.add(user_activity)
    db.session.commit()

    return jsonify({"message": "User added to activity successfully"}), 201


@app.route("/activity/all", methods=["GET"])
def get_all_activities():
    data = request.get_json()
    user_id: int | None = data.get("user_id")

    activities = db.session.scalars(
        select(Activity).where(UserActivity.user_id == user_id)
        if user_id
        else select(Activity)
    ).all()

    activity_list = [
        {
            "id": activity.id,
            "name": activity.name,
            "description": activity.description,
            "type": activity.type,
        }
        for activity in activities
    ]

    return jsonify({"activities": activity_list}), 200


@app.route("/activity/<int:activity_id>/members", methods=["GET"])
def get_activity_members(activity_id):
    activity = db.session.scalar(select(Activity).where(Activity.id == activity_id))
    if not activity:
        return jsonify({"message": "Activity not found"}), 404

    user_activities = db.session.scalars(
        select(UserActivity).where(UserActivity.activity_id == activity_id)
    ).all()

    members = []
    for ua in user_activities:
        user = db.session.scalar(select(User).where(User.id == ua.user_id))
        if user:
            members.append(
                {
                    "user_id": user.id,
                    "username": user.username,
                    "role": ua.role,
                }
            )

    return jsonify({"members": members}), 200


@app.route("/activity/<int:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    activity = db.session.scalar(select(Activity).where(Activity.id == activity_id))
    if not activity:
        return jsonify({"message": "Activity not found"}), 404

    db.session.scalars(
        select(UserActivity).where(UserActivity.activity_id == activity_id)
    ).all()

    for ua in db.session.scalars(
        select(UserActivity).where(UserActivity.activity_id == activity_id)
    ):
        db.session.delete(ua)

    db.session.delete(activity)
    db.session.commit()

    return jsonify({"message": "Activity deleted successfully"}), 200


@app.route("/activity/<int:activity_id>/members/<int:user_id>", methods=["DELETE"])
def remove_user_from_activity(activity_id, user_id):
    user_activity = db.session.scalar(
        select(UserActivity).where(
            UserActivity.user_id == user_id, UserActivity.activity_id == activity_id
        )
    )

    if not user_activity:
        return jsonify({"message": "User not in activity"}), 404

    db.session.delete(user_activity)
    db.session.commit()

    return jsonify({"message": "User removed from activity successfully"}), 200
