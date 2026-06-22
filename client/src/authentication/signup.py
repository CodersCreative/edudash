from typing import Callable, Optional
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor, QIcon
import requests
import routes
from theming.theme import theme

from .styles import STYLES
from assets.icons import icons
import routes


class SignUpScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.open_login: Optional[Callable[[], None]] = None
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === LEFT PANEL ===
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {theme.primary.name()}, stop:1 {theme.danger.name()});
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        """)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.setContentsMargins(40, 40, 40, 40)

        title_label = QLabel("Sign Up")
        title_label.setStyleSheet(
            STYLES["titleTextInverted"] + "; background: transparent;"
        )
        title_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        description = QLabel("Enter your details to create a new account")
        description.setStyleSheet(
            STYLES["normalTextInverted"] + "; background: transparent;"
        )
        description.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        left_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignTop)
        left_layout.addSpacing(20)
        left_layout.addWidget(description)
        left_layout.addSpacing(50)

        # === RIGHT PANEL ===
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            background-color: {theme.background.name()};
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        """)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Close button (top-right)
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        close_btn = QPushButton()
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("border: none;")
        close_btn.setIcon(QIcon(icons.cancel))
        close_btn.setIconSize(QSize(20, 20))
        close_btn.clicked.connect(self.close)
        top_bar.addWidget(close_btn)
        right_layout.addLayout(top_bar)

        # Title
        signup_title = QLabel("Create Account")
        signup_title.setStyleSheet(STYLES["titleText"])
        right_layout.addWidget(signup_title, alignment=Qt.AlignmentFlag.AlignTop)
        right_layout.addSpacing(30)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(STYLES["textBox"])
        right_layout.addWidget(self.username_input)
        right_layout.addSpacing(20)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet(STYLES["textBox"])
        right_layout.addWidget(self.email_input)
        right_layout.addSpacing(20)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(STYLES["textBox"])
        right_layout.addWidget(self.password_input)
        right_layout.addSpacing(20)

        # Confirm password input
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet(STYLES["textBox"])
        right_layout.addWidget(self.confirm_password_input)
        right_layout.addSpacing(40)

        # Sign Up button
        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setStyleSheet(STYLES["mainbutton"])
        right_layout.addWidget(self.signup_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(left_panel, 0, 0)
        layout.addWidget(right_panel, 0, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 3)

        self.signup_btn.clicked.connect(self.handle_sign_up)

    def handle_sign_up(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Validation
        if not username or not email or not password or not confirm_password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return
        if password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        # Send to backend
        try:
            from constants import SERVER_URL

            response = requests.post(
                SERVER_URL + "register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                },
                timeout=5,
            )
            if response.status_code == 200:
                if routes.open_dashboard:
                    if routes.set_user:
                        routes.set_user(
                            routes.User(
                                response.json().get("username", email.split("@")[0]),
                                response.json().get("id", 0),
                                response.json().get("role", 0),
                                response.json().get("points", 0),
                            )
                        )
                    routes.open_dashboard()
            else:
                msg = response.json().get("message", "Registration failed.")
                QMessageBox.warning(self, "Failed", msg)
        except Exception as e:
            print("Registration error:", e)
            QMessageBox.warning(self, "Error", "Could not connect to server.")
