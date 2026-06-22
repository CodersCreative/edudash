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

from assets import icons
from routes import User
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme


class PointsTab(BaseTab):
    def __init__(self, user: User | None = None):
        super().__init__()
        self.user = user
        self.setup_ui()

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

        total_points_label = QLabel(str(points))
        total_points_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 128px;
                font-weight: bold;
                color: {theme.background.name()};
            }}
        """
        )
        total_points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        total_points_frame = QFrame()
        total_points_layout = QVBoxLayout(total_points_frame)
        total_points_layout.addWidget(total_points_label)

        breakdown_frame = QFrame()
        breakdown_layout = QGridLayout(breakdown_frame)

        academics_points = self.create_points_breakdown_item("book.svg", 150)
        cultures_points = self.create_points_breakdown_item("comedy_mask.svg", 75)
        sports_points = self.create_points_breakdown_item("sports.svg", 120)

        breakdown_layout.addWidget(academics_points, 0, 0)
        breakdown_layout.addWidget(cultures_points, 0, 1)
        breakdown_layout.addWidget(sports_points, 0, 2)

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

        history_table = QTableWidget()
        history_table.setColumnCount(3)
        history_table.setRowCount(5)
        history_table.setHorizontalHeaderLabels(["Date", "Activity", "Points"])
        history_table.setStyleSheet(
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

        history_data = [
            ("20/06/2026", "Lorem Ipsum", "+25"),
            ("20/06/2026", "Lorem Ipsum", "-5"),
            ("20/06/2026", "Lorem Ipsum", "+15"),
            ("20/06/2026", "Lorem Ipsum", "+10"),
            ("20/06/2026", "Lorem Ipsum", "+20"),
        ]

        for i, (date, activity, points) in enumerate(history_data):
            history_table.setItem(i, 0, QTableWidgetItem(date))
            history_table.setItem(i, 1, QTableWidgetItem(activity))
            item = QTableWidgetItem(points)
            if "+" in points:
                item.setForeground(theme.secondary)
            else:
                item.setForeground(theme.danger)
            history_table.setItem(i, 2, item)

        history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        history_table.verticalHeader().setVisible(False)
        history_layout.addWidget(history_table)

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

        rewards_table = QTableWidget()
        rewards_table.setColumnCount(3)
        rewards_table.setRowCount(4)
        rewards_table.setHorizontalHeaderLabels(["Reward", "Points Required", "Status"])
        rewards_table.setStyleSheet(
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

        rewards_data = [
            ("20/06/2026", "Lorem Ipsum", "+5"),
            ("20/06/2026", "Lorem Ipsum", "+10"),
            ("20/06/2026", "Lorem Ipsum", "+3"),
        ]

        for i, (date, reason, points) in enumerate(rewards_data):
            rewards_table.setItem(i, 0, QTableWidgetItem(date))
            rewards_table.setItem(i, 1, QTableWidgetItem(reason))
            item = QTableWidgetItem(points)
            item.setForeground(theme.secondary)
            rewards_table.setItem(i, 2, item)

        rewards_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        rewards_table.verticalHeader().setVisible(False)
        rewards_layout.addWidget(rewards_table)

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

        punishments_table = QTableWidget()
        punishments_table.setColumnCount(3)
        punishments_table.setRowCount(3)
        punishments_table.setHorizontalHeaderLabels(["Date", "Reason", "Points"])
        punishments_table.setStyleSheet(
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

        punishments_data = [
            ("20/06/2026", "Lorem Ipsum", "-5"),
            ("20/06/2026", "Lorem Ipsum", "-10"),
            ("20/06/2026", "Lorem Ipsum", "-3"),
        ]

        for i, (date, reason, points) in enumerate(punishments_data):
            punishments_table.setItem(i, 0, QTableWidgetItem(date))
            punishments_table.setItem(i, 1, QTableWidgetItem(reason))
            item = QTableWidgetItem(points)
            item.setForeground(theme.danger)
            punishments_table.setItem(i, 2, item)

        punishments_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        punishments_table.verticalHeader().setVisible(False)
        punishments_layout.addWidget(punishments_table)

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

        points_label = QLabel(f"{points}")
        points_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 64px;
                font-weight: bold;
            }}
        """
        )
        points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(points_label)

        return frame
