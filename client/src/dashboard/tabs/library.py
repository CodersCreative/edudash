from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
)
from PySide6.QtCore import Qt
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme


class LibraryTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search for books...")
        search_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 14px;
                color: {theme.text.name()};
                background: {theme.background_alternative.name()};
                border: 1px solid {theme.primary.name()};
                border-radius: 5px;
                padding: 10px;
            }}
        """)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet(STYLES["mainbutton"])

        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        layout.addStretch()
