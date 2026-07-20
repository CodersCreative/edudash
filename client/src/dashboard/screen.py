from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTabWidget,
)
from PySide6.QtGui import QFont
import routes
from theming.theme import theme
from authentication.styles import STYLES

from .tabs.library import LibraryTab
from .tabs.points import PointsTab
from .tabs.teacher import TeacherTab
from .tabs.leaderboard import LeaderboardTab
from .tabs.calendar import CalendarTab
from .tabs.overview import OverviewTab
from .tabs.student.student_tab import StudentTab


class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.user = None
        if routes.get_user:
            self.user = routes.get_user()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        header = self.create_header()
        main_layout.addWidget(header)

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {theme.background_alternative.name()};
                background: {theme.background.name()};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background: {theme.background_alternative.name()};
                color: {theme.text.name()};
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QTabBar::tab:selected {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
            }}
        """)

        tab_widget.addTab(OverviewTab(self.user), "Overview")
        tab_widget.addTab(LeaderboardTab(), "Leaderboard")
        tab_widget.addTab(LibraryTab(), "Library")
        tab_widget.addTab(CalendarTab(), "Calendar")

        if self.user and self.user.role >= 3:
            tab_widget.addTab(TeacherTab(), "Teacher")
        else:
            tab_widget.addTab(StudentTab(self.user), "Activities")
            tab_widget.addTab(PointsTab(self.user), "Points")

        main_layout.addWidget(tab_widget)

    def create_header(self):
        header = QFrame()
        header.setStyleSheet(f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """)
        header_layout = QHBoxLayout(header)

        username = "Guest"
        if self.user:
            username = self.user.username

        title = QLabel(f"Hello, {username}!")
        title.setStyleSheet(STYLES["titleText"])
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        header_layout.addWidget(title)
        header_layout.addStretch()

        return header
