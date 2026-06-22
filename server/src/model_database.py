from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey
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
