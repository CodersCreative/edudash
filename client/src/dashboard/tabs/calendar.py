from PySide6.QtWidgets import QVBoxLayout, QFrame, QCalendarWidget
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme


class CalendarTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        calendar_frame = QFrame()
        calendar_frame.setStyleSheet(f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 20px;
        """)
        calendar_layout = QVBoxLayout(calendar_frame)

        calendar = QCalendarWidget()
        calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background: {theme.background.name()};
                color: {theme.text.name()};
            }}
            QCalendarWidget QTableView {{
                background: {theme.background.name()};
                color: {theme.text.name()};
                selection-background-color: {theme.primary.name()};
                selection-color: {theme.background.name()};
            }}
        """)
        calendar_layout.addWidget(calendar)

        layout.addWidget(calendar_frame)
        layout.addStretch()
