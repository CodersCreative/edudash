from PySide6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
)
from PySide6.QtCore import Qt
import requests
from routes import User
from ..base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL, ACTIVITY_TYPE_NAMES, ROLE_NAMES


class ManageTab(BaseTab):
    def __init__(self, user: User | None = None):
        super().__init__()
        self.user = user
        self.activity_id = None
        self.activity_data = None
        self.setup_ui()

    def set_activity_id(self, activity_id):
        self.activity_id = activity_id
        self.load_activity_data()

    def load_activity_data(self):
        if not self.activity_id or not self.user:
            return

        try:
            response = requests.get(
                SERVER_URL + "activity/user",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if response.ok:
                data = response.json()
                activities = data.get("activities", [])
                for activity in activities:
                    if activity.get("id") == self.activity_id:
                        self.activity_data = activity
                        self.populate_activity_details()
                        break

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

        self.details_container = QFrame()
        self.details_container.setStyleSheet(
            f"""
            background: {theme.background.name()};
        """
        )
        self.details_layout = QVBoxLayout(self.details_container)
        self.details_layout.setSpacing(15)

        scroll_area.setWidget(self.details_container)
        layout.addWidget(scroll_area)

    def populate_activity_details(self):
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.activity_data:
            self.show_no_activity()
            return

        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 20px;
        """
        )
        header_layout = QVBoxLayout(header_frame)

        header_row = QHBoxLayout()

        name_label = QLabel(self.activity_data.get("name", "Unknown Activity"))
        name_label.setStyleSheet(
            f"""
            font-size: 24px;
            font-weight: bold;
            color: {theme.text.name()};
        """
        )

        type_label = QLabel(
            self.get_activity_type_string(self.activity_data.get("type", 0))
        )
        type_label.setStyleSheet(
            f"""
            font-size: 14px;
            background: {theme.primary.name()};
            color: {theme.background.name()};
            padding: 8px 16px;
            border-radius: 8px;
        """
        )

        header_row.addWidget(name_label)
        header_row.addStretch()
        header_row.addWidget(type_label)

        header_layout.addLayout(header_row)

        description = self.activity_data.get("description", "No description")
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet(
                f"""
                font-size: 14px;
                color: {theme.text.name()};
                padding: 10px 0;
            """
            )
            desc_label.setWordWrap(True)
            header_layout.addWidget(desc_label)

        role = self.activity_data.get("role", 0)
        role_label = QLabel(f"Your Role: {self.get_role_string(role)}")
        role_label.setStyleSheet(
            f"""
            font-size: 14px;
            color: {theme.primary.name()};
            padding: 5px 0;
            font-weight: bold;
        """
        )
        header_layout.addWidget(role_label)

        self.details_layout.addWidget(header_frame)

        members = self.activity_data.get("members", [])
        if members:
            members_frame = QFrame()
            members_frame.setStyleSheet(
                f"""
                background: {theme.background_alternative.name()};
                border-radius: 10px;
                padding: 20px;
            """
            )
            members_layout = QVBoxLayout(members_frame)

            members_table = QTableWidget()
            members_table.setColumnCount(2)
            members_table.setHorizontalHeaderLabels(["Name", "Role"])
            members_table.setStyleSheet(
                f"""
                QTableWidget {{
                    background: {theme.background.name()};
                    color: {theme.text.name()};
                    gridline-color: {theme.background_alternative.name()};
                    border-radius: 5px;
                    font-size: 12px;
                }}
                QHeaderView::section {{
                    background: {theme.primary.name()};
                    color: {theme.background.name()};
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 12px;
                }}
            """
            )
            members_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            members_table.verticalHeader().setVisible(False)

            members_table.setRowCount(len(members))
            for i, member in enumerate(members):
                members_table.setItem(
                    i, 0, QTableWidgetItem(member.get("username", "Unknown"))
                )
                members_table.setItem(
                    i, 1, QTableWidgetItem(self.get_role_string(member.get("role", 0)))
                )

            members_layout.addWidget(members_table)
            self.details_layout.addWidget(members_frame)

        self.details_layout.addStretch()

    def get_activity_type_string(self, activity_type):
        return ACTIVITY_TYPE_NAMES.get(activity_type, "Unknown")

    def get_role_string(self, role):
        return ROLE_NAMES.get(role, "Unknown")

    def show_no_activity(self):
        no_data_label = QLabel("No activity selected")
        no_data_label.setStyleSheet(
            f"""
            font-size: 14px;
            color: {theme.text.name()};
            padding: 20px;
        """
        )
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(no_data_label)
