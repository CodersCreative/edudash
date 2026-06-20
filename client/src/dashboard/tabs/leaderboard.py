from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme


class LeaderboardTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("View by:"))

        leaderboard_type = QComboBox()
        leaderboard_type.addItems(["Overall", "Academics", "Sports", "Cultures"])
        leaderboard_type.setStyleSheet(STYLES["textBox"])
        selector_layout.addWidget(leaderboard_type)
        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setRowCount(10)
        table.setHorizontalHeaderLabels(["Rank", "Student", "Points"])
        table.setStyleSheet(f"""
            QTableWidget {{
                background: {theme.background.name()};
                color: {theme.text.name()};
                gridline-color: {theme.background_alternative.name()};
                border-radius: 5px;
            }}
            QHeaderView::section {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                padding: 5px;
                border-radius: 3px;
            }}
        """)

        students = [
            (1, "Lorem Ipsum", 520),
            (2, "Lorem Ipsum", 485),
            (3, "Lorem Ipsum", 470),
            (4, "Lorem Ipsum", 455),
            (5, "Lorem Ipsum", 440),
            (6, "Lorem Ipsum", 425),
            (7, "Lorem Ipsum", 410),
            (8, "Lorem Ipsum", 395),
            (9, "Lorem Ipsum", 380),
            (10, "Lorem Ipsum", 365),
        ]

        for i, (rank, name, points) in enumerate(students):
            table.setItem(i, 0, QTableWidgetItem(str(rank)))
            table.setItem(i, 1, QTableWidgetItem(name))
            table.setItem(i, 3, QTableWidgetItem(str(points)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table)
