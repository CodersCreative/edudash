from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    DateTime,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

# Roles to be used for activities. All roles above 4 will be treated as a student
STUDENT_ROLE = 0
VICE_CAPTAIN_ROLE = 1
CAPTAIN_ROLE = 2
TEACHER_ROLE = 3
ADMIN_ROLE = 4

ACADEMIC_TYPE = 0
CULTURAL_TYPE = 1
SPORTING_TYPE = 2
OVERALL_TYPE = 3

PERSONAL_CALENDAR_TYPE = 0
ACTIVITY_CALENDAR_TYPE = 1


class User(db.Model):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    profile_picture: Mapped[str | None] = mapped_column(String(248), nullable=True)
    role: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)

    punishments: Mapped[list["Punishment"]] = relationship(
        "Punishment", foreign_keys="Punishment.user_id", back_populates="user"
    )
    punishments_given: Mapped[list["Punishment"]] = relationship(
        "Punishment", foreign_keys="Punishment.teacher_id", back_populates="teacher"
    )
    rewards: Mapped[list["Reward"]] = relationship(
        "Reward", foreign_keys="Reward.user_id", back_populates="user"
    )
    rewards_given: Mapped[list["Reward"]] = relationship(
        "Reward", foreign_keys="Reward.teacher_id", back_populates="teacher"
    )
    activities: Mapped[list["UserActivity"]] = relationship(
        "UserActivity", back_populates="user"
    )
    personal_calendar: Mapped[Optional["Calendar"]] = relationship(
        "Calendar", back_populates="owner", foreign_keys="Calendar.owner_id"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Punishment(db.Model):
    __tablename__ = "Punishment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("User.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("User.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="punishments"
    )
    teacher: Mapped["User"] = relationship(
        "User", foreign_keys=[teacher_id], back_populates="punishments_given"
    )

    def __repr__(self) -> str:
        return f"<Punishment -{self.points} because {self.reason} to {self.user_id}>"


class Reward(db.Model):
    __tablename__ = "Reward"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("User.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("User.id"), nullable=False
    )
    activity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("Activity.id"), nullable=True
    )
    reason: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="rewards"
    )
    teacher: Mapped["User"] = relationship(
        "User", foreign_keys=[teacher_id], back_populates="rewards_given"
    )
    activity: Mapped[Optional["Activity"]] = relationship(
        "Activity", back_populates="rewards"
    )

    def __repr__(self) -> str:
        return f"<Reward +{self.points} because {self.reason} to {self.user_id}>"


class Book(db.Model):
    __tablename__ = "Book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("User.id"), nullable=True
    )
    isbn13: Mapped[str | None] = mapped_column(String(120), nullable=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1200), nullable=True)
    file: Mapped[str] = mapped_column(String(248), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    is_public: Mapped[bool] = mapped_column(default=True, nullable=False)

    owner: Mapped[Optional["User"]] = relationship("User", foreign_keys=[owner_id])

    __table_args__ = (
        CheckConstraint(
            "file_type in ('pdf', 'epub', 'markdown')", name="book_file_type"
        ),
        UniqueConstraint("title", "author", "file", name="uq_book_resource"),
    )

    def __repr__(self) -> str:
        return f"<Book {self.title}>"


class BookProgress(db.Model):
    __tablename__ = "BookProgress"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("User.id"), primary_key=True, nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Book.id"), primary_key=True, nullable=False
    )
    page: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scroll: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User")
    book: Mapped["Book"] = relationship("Book")

    def __repr__(self) -> str:
        return (
            f"<BookProgress user={self.user_id} book={self.book_id} page={self.page}>"
        )


class Activity(db.Model):
    __tablename__ = "Activity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(120), nullable=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)

    rewards: Mapped[list["Reward"]] = relationship("Reward", back_populates="activity")
    user_activities: Mapped[list["UserActivity"]] = relationship(
        "UserActivity", back_populates="activity"
    )
    calendar: Mapped[Optional["Calendar"]] = relationship(
        "Calendar", back_populates="activity", foreign_keys="Calendar.activity_id"
    )

    def __repr__(self) -> str:
        return f"<Activity {self.name}>"


class UserActivity(db.Model):
    __tablename__ = "UserActivity"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("User.id"), primary_key=True, nullable=False
    )
    activity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Activity.id"), primary_key=True, nullable=False
    )
    role: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="activities")
    activity: Mapped["Activity"] = relationship(
        "Activity", back_populates="user_activities"
    )

    def __repr__(self) -> str:
        return f"<UserActivity {self.user_id} to {self.activity_id}>"


class Calendar(db.Model):
    __tablename__ = "Calendar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("User.id"), nullable=True
    )
    activity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("Activity.id"), nullable=True
    )

    owner: Mapped[Optional["User"]] = relationship(
        "User", back_populates="personal_calendar", foreign_keys=[owner_id]
    )
    activity: Mapped[Optional["Activity"]] = relationship(
        "Activity", back_populates="calendar", foreign_keys=[activity_id]
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="calendar")

    __table_args__ = (
        CheckConstraint(
            "(owner_id IS NOT NULL AND activity_id IS NULL) OR (owner_id IS NULL AND activity_id IS NOT NULL)",
            name="calendar_owner_or_activity",
        ),
    )

    def __repr__(self) -> str:
        return f"<Calendar {self.name}>"


class Event(db.Model):
    __tablename__ = "Event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    calendar_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Calendar.id"), nullable=False
    )
    is_synced: Mapped[bool] = mapped_column(default=False, nullable=False)
    source_event_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    activity_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    calendar: Mapped["Calendar"] = relationship("Calendar", back_populates="events")

    def __repr__(self) -> str:
        return f"<Event {self.title} at {self.start_time}>"
