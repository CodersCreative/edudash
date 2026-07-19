from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt
import requests
from datetime import datetime
from assets import icons
from routes import User
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL


class PointsTab(BaseTab):
    def __init__(self, user: User | None = None):
        super().__init__()
        self.user = user
        self.setup_ui()
        self.load_points_data()

    def load_points_data(self):
        if not self.user:
            return

        try:
            overall_response = requests.get(
                SERVER_URL + "overall/points",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if overall_response.ok:
                overall_data = overall_response.json()
                self.total_points_label.setText(str(overall_data.get("points", 0)))

            academics_response = requests.get(
                SERVER_URL + "academic/points",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if academics_response.ok:
                academics_data = academics_response.json()
                self.academics_points.points_label.setText(
                    str(academics_data.get("points", 0))
                )

            sports_response = requests.get(
                SERVER_URL + "sports/points", json={"user_id": self.user.id}, timeout=10
            )

            if sports_response.ok:
                sports_data = sports_response.json()
                self.sports_points.points_label.setText(
                    str(sports_data.get("points", 0))
                )

            cultural_response = requests.get(
                SERVER_URL + "cultural/points",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if cultural_response.ok:
                cultural_data = cultural_response.json()
                self.cultures_points.points_label.setText(
                    str(cultural_data.get("points", 0))
                )

            history_response = requests.get(
                SERVER_URL + "overall/history",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if history_response.ok:
                history_data = history_response.json()
                self.populate_history_table(history_data.get("history", []))

            rewards_response = requests.get(
                SERVER_URL + "rewards/history",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if rewards_response.ok:
                rewards_data = rewards_response.json()
                self.populate_rewards_table(rewards_data.get("history", []))

            punishments_response = requests.get(
                SERVER_URL + "punish/history",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if punishments_response.ok:
                punishments_data = punishments_response.json()
                self.populate_punishments_table(punishments_data.get("history", []))

        except Exception as e:
            print(f"Error loading data: {e}")

    def setup_ui(self):
        layout = QVBoxLayout(self)

        summary_frame = QFrame()
        summary_frame.setStyleSheet(
            f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {theme.primary.name()}, stop:1 {theme.secondary.name()});
            border-radius: 15px;
            padding: 0px;
        """
        )
        summary_layout = QHBoxLayout(summary_frame)

        points = 0
        if self.user:
            points = self.user.points

        self.total_points_label = QLabel(str(points))
        self.total_points_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 128px;
                font-weight: bold;
                color: {theme.background.name()};
            }}
        """
        )
        self.total_points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        total_points_frame = QFrame()
        total_points_layout = QVBoxLayout(total_points_frame)
        total_points_layout.addWidget(self.total_points_label)

        breakdown_frame = QFrame()
        breakdown_layout = QGridLayout(breakdown_frame)

        self.academics_points = self.create_points_breakdown_item("book.svg", 0)
        self.cultures_points = self.create_points_breakdown_item("comedy_mask.svg", 0)
        self.sports_points = self.create_points_breakdown_item("sports.svg", 0)

        breakdown_layout.addWidget(self.academics_points, 0, 0)
        breakdown_layout.addWidget(self.cultures_points, 0, 1)
        breakdown_layout.addWidget(self.sports_points, 0, 2)

        summary_layout.addWidget(total_points_frame, 1)
        summary_layout.addWidget(breakdown_frame, 2)

        layout.addWidget(summary_frame)
        layout.addSpacing(20)

        details_layout = QHBoxLayout()

        history_frame = QFrame()
        history_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """
        )
        history_layout = QVBoxLayout(history_frame)

        history_title = QLabel("History")
        history_title.setStyleSheet(STYLES["titleText"])
        history_layout.addWidget(history_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Date", "Activity", "Points"])
        self.history_table.setStyleSheet(
            f"""
            QTableWidget {{
                background: {theme.background.name()};
                color: {theme.text.name()};
                gridline-color: {theme.background_alternative.name()};
                border-radius: 5px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                padding: 3px;
                border-radius: 3px;
                font-size: 11px;
            }}
        """
        )

        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.history_table.verticalHeader().setVisible(False)
        history_layout.addWidget(self.history_table)

        rewards_frame = QFrame()
        rewards_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """
        )
        rewards_layout = QVBoxLayout(rewards_frame)

        rewards_title = QLabel("Rewards")
        rewards_title.setStyleSheet(STYLES["titleText"])
        rewards_layout.addWidget(rewards_title)

        self.rewards_table = QTableWidget()
        self.rewards_table.setColumnCount(3)
        self.rewards_table.setHorizontalHeaderLabels(["Reason", "Points", "Activity"])
        self.rewards_table.setStyleSheet(
            f"""
            QTableWidget {{
                background: {theme.background.name()};
                color: {theme.text.name()};
                gridline-color: {theme.background_alternative.name()};
                border-radius: 5px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                padding: 3px;
                border-radius: 3px;
                font-size: 11px;
            }}
        """
        )

        self.rewards_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.rewards_table.verticalHeader().setVisible(False)
        rewards_layout.addWidget(self.rewards_table)

        punishments_frame = QFrame()
        punishments_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """
        )
        punishments_layout = QVBoxLayout(punishments_frame)

        punishments_title = QLabel("Punishments")
        punishments_title.setStyleSheet(STYLES["titleText"])
        punishments_layout.addWidget(punishments_title)

        self.punishments_table = QTableWidget()
        self.punishments_table.setColumnCount(2)
        self.punishments_table.setHorizontalHeaderLabels(["Reason", "Points"])
        self.punishments_table.setStyleSheet(
            f"""
            QTableWidget {{
                background: {theme.background.name()};
                color: {theme.text.name()};
                gridline-color: {theme.background_alternative.name()};
                border-radius: 5px;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                padding: 3px;
                border-radius: 3px;
                font-size: 11px;
            }}
        """
        )

        self.punishments_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.punishments_table.verticalHeader().setVisible(False)
        punishments_layout.addWidget(self.punishments_table)

        details_layout.addWidget(history_frame, 1)
        details_layout.addWidget(rewards_frame, 1)
        details_layout.addWidget(punishments_frame, 1)

        layout.addLayout(details_layout)

    def create_points_breakdown_item(self, icon_path, points):
        frame = QFrame()

        frame.setStyleSheet(
            f"""
            background: {theme.background.name()};
            border-radius: 15px;
            padding: 30px;
        """
        )
        layout = QHBoxLayout(frame)

        icon = icons.get_icon(icon_path, 64)

        frame.points_label = QLabel(f"{points}")
        frame.points_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 64px;
                font-weight: bold;
            }}
        """
        )
        frame.points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(frame.points_label)

        return frame

    def populate_history_table(self, history):
        self.history_table.setRowCount(len(history))

        if not history:
            self.history_table.setRowCount(1)
            item = QTableWidgetItem("No data available")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_table.setItem(0, 0, item)
            self.history_table.setSpan(0, 0, 1, 3)
            return

        for i, entry in enumerate(history):
            entry_type = entry.get("type", "")
            reason = entry.get("reason", "Unknown")
            points = entry.get("points", 0)

            date_str = datetime.now().strftime("%d/%m/%Y")

            self.history_table.setItem(i, 0, QTableWidgetItem(date_str))
            self.history_table.setItem(i, 1, QTableWidgetItem(reason))

            points_str = f"+{points}" if points > 0 else str(points)

            item = QTableWidgetItem(points_str)
            if points > 0:
                item.setForeground(theme.secondary)
            else:
                item.setForeground(theme.danger)

            self.history_table.setItem(i, 2, item)

    def populate_rewards_table(self, rewards):
        self.rewards_table.setRowCount(len(rewards))

        if not rewards:
            self.rewards_table.setRowCount(1)
            item = QTableWidgetItem("No data available")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rewards_table.setItem(0, 0, item)
            self.rewards_table.setSpan(0, 0, 1, 3)
            return

        for i, reward in enumerate(rewards):
            reason = reward.get("reason", "Unknown")
            points = reward.get("points", 0)
            activity_id = reward.get("activity_id")

            self.rewards_table.setItem(i, 0, QTableWidgetItem(reason))
            item = QTableWidgetItem(f"+{points}")
            item.setForeground(theme.secondary)
            self.rewards_table.setItem(i, 1, item)

            activity_str = str(activity_id) if activity_id else "N/A"
            self.rewards_table.setItem(i, 2, QTableWidgetItem(activity_str))

    def populate_punishments_table(self, punishments):
        self.punishments_table.setRowCount(len(punishments))

        if not punishments:
            self.punishments_table.setRowCount(1)
            item = QTableWidgetItem("No data available")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.punishments_table.setItem(0, 0, item)
            self.punishments_table.setSpan(0, 0, 1, 2)
            return

        for i, punishment in enumerate(punishments):
            reason = punishment.get("reason", "Unknown")
            points = punishment.get("points", 0)

            self.punishments_table.setItem(i, 0, QTableWidgetItem(reason))
            item = QTableWidgetItem(f"-{points}")
            item.setForeground(theme.danger)
            self.punishments_table.setItem(i, 1, item)
