from pathlib import Path
from werkzeug.utils import secure_filename
from sqlalchemy import select, func
from model_database import db, User, Activity, Reward
from flask import Response, jsonify
import google_books_api_wrapper.api as books
from app import GOOGLE_BOOKS_CLIENT

def get_username(id: int | None = None, email: str | None = None) -> str | None:
    user = None
    if email is None:
        user = db.session.scalar(select(User).where(User.id == id))
    elif id is None:
        user = db.session.scalar(select(User).where(User.email == email))

    if not user:
        return None

    return user.username

def get_book_details(title : str | None = None, isbn13: str | None = None, isbn10: str | None = None) -> books.Book | None:
    try:
        if isbn10:
            return GOOGLE_BOOKS_CLIENT.get_book_by_isbn10(isbn10);
        elif isbn13:
            return GOOGLE_BOOKS_CLIENT.get_book_by_isbn13(isbn13);
        elif title:
            return GOOGLE_BOOKS_CLIENT.get_book_by_title(title);
    except Exception:
        return None
    return None

def update_users_points(
    new_points: int, id: int | None = None, email: str | None = None
) -> tuple[Response, int]:
    user = None
    if email is None:
        user = db.session.scalar(select(User).where(User.id == id))
    elif id is None:
        user = db.session.scalar(select(User).where(User.email == email))

    if not user:
        return jsonify({"message": "User not found"}), 404

    if new_points > user.points:
        user.points += new_points
        db.session.commit()

    return jsonify({"message": "Points updated"}), 200


def get_points_by_activity_type(user_id: int, activity_type: int) -> int:
    points = 0
    activities = db.session.scalars(
        select(Activity.id).where(Activity.type == activity_type)
    ).all()

    for activity_id in activities:
        activity_points = (
            db.session.scalar(
                select(func.sum(Reward.points))
                .where(Reward.user_id == user_id)
                .where(Reward.activity_id == activity_id)
            )
            or 0
        )
        points += activity_points

    return points


def get_leaderboard_by_activity_type(activity_type: int) -> list[dict]:
    users = db.session.scalars(select(User)).all()
    leaderboard = []

    for user in users:
        points = get_points_by_activity_type(user.id, activity_type)
        if points > 0:
            leaderboard.append({"username": user.username, "points": points})

    leaderboard.sort(key=lambda x: x["points"], reverse=True)

    for rank, entry in enumerate(leaderboard, start=1):
        entry["rank"] = rank

    return leaderboard


def get_user_by_id_or_email(
    user_id: int | None = None, email: str | None = None
) -> User | None:
    user = None
    if email is None:
        user = db.session.scalar(select(User).where(User.id == user_id))
    elif user_id is None:
        user = db.session.scalar(select(User).where(User.email == email))
    return user


def get_project_path() -> Path:
    return Path(__file__).parent.parent


def get_library_path() -> Path:
    path = get_project_path() / "src" / "instance" / "library"
    path.mkdir(parents=True, exist_ok=True)
    return path


def allowed_book_extension(filename: str) -> bool:
    return filename.rsplit(".", 1)[-1].lower() in {"pdf", "epub", "md", "markdown"}


def normalize_book_extension(filename: str) -> str:
    suffix = filename.rsplit(".", 1)[-1].lower()
    return "markdown" if suffix in {"md", "markdown"} else suffix


def safe_book_filename(title: str, author: str, filename: str) -> str:
    base = secure_filename(f"{author}-{title}") or "book"
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"{base}.{ext}"
