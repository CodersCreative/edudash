from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
    QPushButton,
)
from PySide6.QtCore import Qt
import requests
from routes import User
from ..base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL, ACTIVITY_TYPE_NAMES, ROLE_NAMES


class ActivitiesTab(BaseTab):
    def __init__(self, user: User | None = None, parent=None):
        super().__init__()
        self.user = user
        self.parent = parent
        self.setup_ui()
        self.load_activity_data()

    def load_activity_data(self):
        if not self.user:
            return

        try:
            response = requests.get(
                SERVER_URL + "activity/user",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if response.ok:
                data = response.json()
                self.populate_activities(data.get("activities", []))

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Error", f"Failed to load activity: {e}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background: {theme.background.name()};
            }}
        """
        )

        self.activities_container = QFrame()
        self.activities_container.setStyleSheet(
            f"""
            background: {theme.background.name()};
        """
        )
        self.activities_layout = QVBoxLayout(self.activities_container)
        self.activities_layout.setSpacing(10)
        self.activities_layout.addStretch()

        scroll_area.setWidget(self.activities_container)
        layout.addWidget(scroll_area)

    def populate_activities(self, activities):
        while self.activities_layout.count() > 1:
            item = self.activities_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not activities:
            self.show_no_activities()
            return

        for activity in activities:
            activity_frame = self.create_activity_card(activity)
            self.activities_layout.insertWidget(
                self.activities_layout.count() - 1, activity_frame
            )

    def create_activity_card(self, activity):
        frame = QFrame()
        frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """
        )
        layout = QVBoxLayout(frame)

        header_layout = QHBoxLayout()

        name_label = QLabel(activity.get("name", "Unknown Activity"))
        name_label.setStyleSheet(
            f"""
            font-size: 16px;
            font-weight: bold;
            color: {theme.text.name()};
        """
        )

        type_label = QLabel(self.get_activity_type_string(activity.get("type", 0)))
        type_label.setStyleSheet(
            f"""
            font-size: 12px;
            background: {theme.primary.name()};
            color: {theme.background.name()};
            padding: 5px 10px;
            border-radius: 5px;
        """
        )

        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(type_label)

        layout.addLayout(header_layout)

        description = activity.get("description", "No description")
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet(
                f"""
                font-size: 12px;
                color: {theme.text.name()};
                padding: 5px 0;
            """
            )
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        role = activity.get("role", 0)
        role_label = QLabel(f"Your Role: {self.get_role_string(role)}")
        role_label.setStyleSheet(
            f"""
            font-size: 12px;
            color: {theme.primary.name()};
            padding: 5px 0;
        """
        )
        layout.addWidget(role_label)

        view_button = QPushButton("View Details")
        view_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {theme.secondary.name()};
            }}
        """
        )
        view_button.clicked.connect(
            lambda: self.open_activity_details(activity.get("id"))
        )
        layout.addWidget(view_button)

        return frame

    def open_activity_details(self, activity_id):
        if self.parent:
            self.parent.open_activity_details(activity_id)

    def get_activity_type_string(self, activity_type):
        return ACTIVITY_TYPE_NAMES.get(activity_type, "Unknown")

    def get_role_string(self, role):
        return ROLE_NAMES.get(role, "Unknown")

    def show_no_activities(self):
        no_data_label = QLabel("You are not part of any activities")
        no_data_label.setStyleSheet(
            f"""
            font-size: 14px;
            color: {theme.text.name()};
            padding: 20px;
        """
        )
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activities_layout.insertWidget(0, no_data_label)
