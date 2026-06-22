from enum import Enum
from PySide6 import QtWidgets
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QMainWindow,
    QStackedWidget,
    QTabWidget,
    QWidget,
)

from utils import get_project_path
from theming.theme import get_palette_from_theme, theme
import routes
from routes import User
from constants import *
import sys
import subprocess
import os


class Screens(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.dock = None

        self.setup_routes()
        self.setup_screens()

    def setup_routes(self):
        routes.open_signup = self.open_signup_screen
        routes.open_login = self.open_login_screen
        routes.open_dashboard = self.open_dashboard_screen
        routes.set_user = self.set_user
        routes.get_user = self.get_user

    def setup_screens(self):
        from authentication.login import LoginScreen

        self.login = LoginScreen()
        self.addWidget(self.login)

        from authentication.signup import SignUpScreen

        self.signup = SignUpScreen()
        self.addWidget(self.signup)

        from dashboard.screen import DashboardScreen

        self.dashboard = DashboardScreen()
        self.addWidget(self.dashboard)

    def open_screen(self, index: int):
        if self.dock is None:
            pass
        else:
            window.removeDockWidget(self.dock)
        self.setCurrentIndex(index)

    def open_login_screen(self):
        self.open_screen(LOGIN)

    def open_signup_screen(self):
        self.open_screen(SIGNUP)

    def open_dashboard_screen(self):
        from dashboard.screen import DashboardScreen

        self.dashboard.close()
        self.removeWidget(self.dashboard)
        self.dashboard = DashboardScreen()
        self.insertWidget(DASHBOARD, self.dashboard)
        self.open_screen(DASHBOARD)

    def set_user(self, user: User):
        self.user = user
        os.environ["uid9"] = str(user.id)

    def get_user(self) -> User:
        return self.user


class ExtraMainScreen(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(1280, 720)
        self.screens = Screens(parent=self)
        self.setCentralWidget(self.screens)
        routes.set_background_style = self.setStyleSheet
        routes.reset_palette = lambda: self.setPalette(get_palette_from_theme(theme))
        routes.set_colour_role = lambda x: self.setBackgroundRole(x)
        self.setPalette(get_palette_from_theme(theme))


app = QApplication(sys.argv)
window = ExtraMainScreen()
window.show()
sys.exit(app.exec())
