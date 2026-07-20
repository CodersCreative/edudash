from flask import jsonify, request
from sqlalchemy import select
from datetime import datetime
from model_database import (
    db,
    User,
    Calendar,
    Event,
    Activity,
    UserActivity,
    PERSONAL_CALENDAR_TYPE,
    ACTIVITY_CALENDAR_TYPE,
)
from utils import get_user_by_id_or_email
from app import app


@app.route("/calendar/personal", methods=["GET"])
def get_personal_calendar():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    user = get_user_by_id_or_email(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.owner_id == user_id, Calendar.type == PERSONAL_CALENDAR_TYPE
        )
    )

    if not calendar:
        return jsonify({"calendar": None, "events": []}), 200

    events = db.session.scalars(
        select(Event).where(Event.calendar_id == calendar.id)
    ).all()

    events_data = [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "is_synced": event.is_synced,
            "source_event_id": event.source_event_id,
            "activity_name": event.activity_name,
        }
        for event in events
    ]

    return jsonify(
        {
            "calendar": {
                "id": calendar.id,
                "name": calendar.name,
                "description": calendar.description,
                "type": calendar.type,
            },
            "events": events_data,
        }
    ), 200


@app.route("/calendar/personal", methods=["POST"])
def create_personal_calendar():
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name", "Personal Calendar")
    description = data.get("description", "")

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    user = get_user_by_id_or_email(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    existing_calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.owner_id == user_id, Calendar.type == PERSONAL_CALENDAR_TYPE
        )
    )

    if existing_calendar:
        return jsonify({"message": "Personal calendar already exists"}), 400

    calendar = Calendar(
        name=name,
        description=description,
        type=PERSONAL_CALENDAR_TYPE,
        owner_id=user_id,
    )
    db.session.add(calendar)
    db.session.commit()

    return jsonify(
        {
            "message": "Personal calendar created successfully",
            "calendar_id": calendar.id,
        }
    ), 201


@app.route("/calendar/personal", methods=["PUT"])
def update_personal_calendar():
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")
    description = data.get("description")

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.owner_id == user_id, Calendar.type == PERSONAL_CALENDAR_TYPE
        )
    )

    if not calendar:
        return jsonify({"message": "Personal calendar not found"}), 404

    if name is not None:
        calendar.name = name
    if description is not None:
        calendar.description = description

    db.session.commit()

    return jsonify({"message": "Personal calendar updated successfully"}), 200


@app.route("/calendar/event", methods=["POST"])
def create_event():
    data = request.get_json()
    calendar_id = data.get("calendar_id")
    title = data.get("title")
    description = data.get("description")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    location = data.get("location")
    is_synced = data.get("is_synced", False)
    source_event_id = data.get("source_event_id")

    if not calendar_id or not title or not start_time or not end_time:
        return (
            jsonify(
                {"message": "Calendar ID, title, start time, and end time are required"}
            ),
            400,
        )

    calendar = db.session.scalar(select(Calendar).where(Calendar.id == calendar_id))
    if not calendar:
        return jsonify({"message": "Calendar not found"}), 404

    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({"message": "Invalid datetime format"}), 400

    event = Event(
        title=title,
        description=description,
        start_time=start_dt,
        end_time=end_dt,
        location=location,
        calendar_id=calendar_id,
        is_synced=is_synced,
        source_event_id=source_event_id,
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "Event created successfully", "event_id": event.id}), 201


@app.route("/calendar/event/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    location = data.get("location")

    event = db.session.scalar(select(Event).where(Event.id == event_id))
    if not event:
        return jsonify({"message": "Event not found"}), 404

    if title is not None:
        event.title = title
    if description is not None:
        event.description = description
    if start_time is not None:
        try:
            event.start_time = datetime.fromisoformat(start_time)
        except ValueError:
            return jsonify({"message": "Invalid datetime format"}), 400
    if end_time is not None:
        try:
            event.end_time = datetime.fromisoformat(end_time)
        except ValueError:
            return jsonify({"message": "Invalid datetime format"}), 400
    if location is not None:
        event.location = location

    db.session.commit()

    return jsonify({"message": "Event updated successfully"}), 200


@app.route("/calendar/event/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = db.session.scalar(select(Event).where(Event.id == event_id))
    if not event:
        return jsonify({"message": "Event not found"}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({"message": "Event deleted successfully"}), 200


@app.route("/calendar/events/month", methods=["GET"])
def get_events_by_month():
    data = request.get_json()
    user_id = data.get("user_id")
    year = data.get("year")
    month = data.get("month")

    if not user_id or not year or not month:
        return jsonify({"message": "User ID, year, and month are required"}), 400

    calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.owner_id == user_id, Calendar.type == PERSONAL_CALENDAR_TYPE
        )
    )

    if not calendar:
        return jsonify({"events": []}), 200

    events = db.session.scalars(
        select(Event).where(
            Event.calendar_id == calendar.id,
            Event.start_time >= datetime(year, month, 1),
            Event.start_time < datetime(year, month + 1, 1)
            if month < 12
            else datetime(year + 1, 1, 1),
        )
    ).all()

    events_data = [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "is_synced": event.is_synced,
            "source_event_id": event.source_event_id,
        }
        for event in events
    ]

    return jsonify({"events": events_data}), 200


@app.route("/calendar/activity", methods=["POST"])
def create_activity_calendar():
    data = request.get_json()
    activity_id = data.get("activity_id")
    name = data.get("name")
    description = data.get("description")

    if not activity_id:
        return jsonify({"message": "Activity ID is required"}), 400

    activity = db.session.scalar(select(Activity).where(Activity.id == activity_id))
    if not activity:
        return jsonify({"message": "Activity not found"}), 404

    existing_calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.activity_id == activity_id, Calendar.type == ACTIVITY_CALENDAR_TYPE
        )
    )

    if existing_calendar:
        return jsonify({"message": "Activity calendar already exists"}), 400

    calendar = Calendar(
        name=name or f"{activity.name} Calendar",
        description=description,
        type=ACTIVITY_CALENDAR_TYPE,
        activity_id=activity_id,
    )
    db.session.add(calendar)
    db.session.commit()

    return jsonify(
        {
            "message": "Activity calendar created successfully",
            "calendar_id": calendar.id,
        }
    ), 201


@app.route("/calendar/activity/<int:activity_id>", methods=["GET"])
def get_activity_calendar(activity_id):
    calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.activity_id == activity_id, Calendar.type == ACTIVITY_CALENDAR_TYPE
        )
    )

    if not calendar:
        return jsonify({"calendar": None, "events": []}), 200

    events = db.session.scalars(
        select(Event).where(Event.calendar_id == calendar.id)
    ).all()

    events_data = [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "is_synced": event.is_synced,
            "source_event_id": event.source_event_id,
        }
        for event in events
    ]

    return jsonify(
        {
            "calendar": {
                "id": calendar.id,
                "name": calendar.name,
                "description": calendar.description,
                "type": calendar.type,
            },
            "events": events_data,
        }
    ), 200


@app.route("/calendar/activity/<int:activity_id>", methods=["PUT"])
def update_activity_calendar(activity_id):
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")

    calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.activity_id == activity_id, Calendar.type == ACTIVITY_CALENDAR_TYPE
        )
    )

    if not calendar:
        return jsonify({"message": "Activity calendar not found"}), 404

    if name is not None:
        calendar.name = name
    if description is not None:
        calendar.description = description

    db.session.commit()

    return jsonify({"message": "Activity calendar updated successfully"}), 200


@app.route("/calendar/sync", methods=["POST"])
def sync_activity_events_to_users():
    data = request.get_json()
    activity_id = data.get("activity_id")

    if not activity_id:
        return jsonify({"message": "Activity ID is required"}), 400

    activity = db.session.scalar(select(Activity).where(Activity.id == activity_id))
    if not activity:
        return jsonify({"message": "Activity not found"}), 404

    activity_calendar = db.session.scalar(
        select(Calendar).where(
            Calendar.activity_id == activity_id, Calendar.type == ACTIVITY_CALENDAR_TYPE
        )
    )

    if not activity_calendar:
        return jsonify({"message": "Activity calendar not found"}), 404

    activity_events = db.session.scalars(
        select(Event).where(Event.calendar_id == activity_calendar.id)
    ).all()

    user_activities = db.session.scalars(
        select(UserActivity).where(UserActivity.activity_id == activity_id)
    ).all()

    synced_count = 0
    for user_activity in user_activities:
        user = db.session.scalar(select(User).where(User.id == user_activity.user_id))
        if not user:
            continue

        personal_calendar = db.session.scalar(
            select(Calendar).where(
                Calendar.owner_id == user.id, Calendar.type == PERSONAL_CALENDAR_TYPE
            )
        )

        if not personal_calendar:
            continue

        for activity_event in activity_events:
            existing_synced = db.session.scalar(
                select(Event).where(
                    Event.calendar_id == personal_calendar.id,
                    Event.source_event_id == activity_event.id,
                )
            )

            if existing_synced:
                continue

            synced_event = Event(
                title=activity_event.title,
                description=activity_event.description,
                start_time=activity_event.start_time,
                end_time=activity_event.end_time,
                location=activity_event.location,
                calendar_id=personal_calendar.id,
                is_synced=True,
                source_event_id=activity_event.id,
                activity_name=activity.name,
            )
            db.session.add(synced_event)
            synced_count += 1

    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Successfully synced {synced_count} events to {len(user_activities)} users"
            }
        ),
        200,
    )


@app.route("/calendar/sync/event/<int:event_id>", methods=["POST"])
def sync_single_event_to_users(event_id):
    data = request.get_json()

    event = db.session.scalar(select(Event).where(Event.id == event_id))
    if not event:
        return jsonify({"message": "Event not found"}), 404

    calendar = db.session.scalar(
        select(Calendar).where(Calendar.id == event.calendar_id)
    )
    if not calendar or calendar.type != ACTIVITY_CALENDAR_TYPE:
        return jsonify({"message": "Event is not from an activity calendar"}), 400

    activity = db.session.scalar(
        select(Activity).where(Activity.id == calendar.activity_id)
    )
    if not activity:
        return jsonify({"message": "Activity not found"}), 404

    user_activities = db.session.scalars(
        select(UserActivity).where(UserActivity.activity_id == activity.id)
    ).all()

    synced_count = 0
    for user_activity in user_activities:
        user = db.session.scalar(select(User).where(User.id == user_activity.user_id))
        if not user:
            continue

        personal_calendar = db.session.scalar(
            select(Calendar).where(
                Calendar.owner_id == user.id, Calendar.type == PERSONAL_CALENDAR_TYPE
            )
        )

        if not personal_calendar:
            continue

        existing_synced = db.session.scalar(
            select(Event).where(
                Event.calendar_id == personal_calendar.id,
                Event.source_event_id == event.id,
            )
        )

        if existing_synced:
            continue

        synced_event = Event(
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            calendar_id=personal_calendar.id,
            is_synced=True,
            source_event_id=event.id,
            activity_name=activity.name,
        )
        db.session.add(synced_event)
        synced_count += 1

    db.session.commit()

    return (
        jsonify({"message": f"Successfully synced event to {synced_count} users"}),
        200,
    )
