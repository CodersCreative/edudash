from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Roles to be used for activities. All roles above 4 will be treated as a student
STUDENT_ROLE = 0
VICE_CAPTAIN_ROLE = 1
CAPTAIN_ROLE = 2
TEACHER_ROLE = 3
ADMIN_ROLE = 4


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(248))
    role = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<User {self.username}>"


class Punishment(db.Model):
    __tablename__ = "Punishment"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    reason = db.Column(db.String(512), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Punishment -{self.points} because {self.reason} to {self.user_id}>"


class Reward(db.Model):
    __tablename__ = "Reward"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("Activity.id"))
    reason = db.Column(db.String(512), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Reward +{self.points} because {self.reason} to {self.user_id}>"


class Activity(db.Model):
    __tablename__ = "Activity"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120))
    type = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Activity {self.name}>"


class UserActivity(db.Model):
    __tablename__ = "UserActivity"
    user_id = db.Column(
        db.Integer, db.ForeignKey("User.id"), primary_key=True, nullable=False
    )
    activity_id = db.Column(
        db.Integer, db.ForeignKey("Activity.id"), primary_key=True, nullable=False
    )
    role = db.Column(db.Integer)

    def __repr__(self):
        return f"<UserActivity {self.user_id} to {self.activity_id}>"
