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
import requests
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL
import routes


class LeaderboardTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_leaderboard("overall")

    def setup_ui(self):
        layout = QVBoxLayout(self)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("View by:"))

        self.leaderboard_type = QComboBox()
        self.leaderboard_type.addItems(["Overall", "Academics", "Sports", "Cultures"])
        self.leaderboard_type.setStyleSheet(STYLES["textBox"])
        self.leaderboard_type.currentTextChanged.connect(self.load_leaderboard)
        selector_layout.addWidget(self.leaderboard_type)
        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rank", "Student", "Points"])
        self.table.setStyleSheet(f"""
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

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table)

    def load_leaderboard(self, leaderboard_type):
        try:
            endpoint_map = {
                "overall": "overall/leaderboard",
                "academic": "academic/leaderboard",
                "sports": "sports/leaderboard",
                "cultural": "cultural/leaderboard",
            }
            endpoint = endpoint_map.get(leaderboard_type.lower(), "overall/leaderboard")

            response = requests.get(SERVER_URL + endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()
            leaderboard = data.get("leaderboard", [])
            self.populate_table(leaderboard)
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Error"))
            self.table.setItem(0, 1, QTableWidgetItem(str(e)))
            self.table.setItem(0, 2, QTableWidgetItem(""))

    def populate_table(self, leaderboard):
        self.table.setRowCount(len(leaderboard))

        if not leaderboard:
            self.table.setRowCount(1)
            item = QTableWidgetItem("No data available")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 3)
            return

        for i, entry in enumerate(leaderboard):
            rank = entry.get("rank", i + 1)
            username = entry.get("username", "Unknown")
            points = entry.get("points", 0)

            self.table.setItem(i, 0, QTableWidgetItem(str(rank)))
            self.table.setItem(i, 1, QTableWidgetItem(username))
            self.table.setItem(i, 2, QTableWidgetItem(str(points)))
