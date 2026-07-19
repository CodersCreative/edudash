from PySide6.QtWidgets import (
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
import routes
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL


class ActivitiesTab(QFrame):
    def __init__(self, parent=None, on_open_activity_details=None):
        super().__init__(parent)
        self.user = None
        if routes.get_user:
            self.user = routes.get_user()
        self.on_open_activity_details = on_open_activity_details
        self.setup_ui()
        self.load_activities()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(4)
        self.activities_table.setHorizontalHeaderLabels(
            ["Name", "Type", "Members", "Actions"]
        )
        self.activities_table.setStyleSheet(f"""
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

        self.activities_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.activities_table.verticalHeader().setVisible(False)
        layout.addWidget(self.activities_table)

    def load_activities(self):
        try:
            response = requests.get(
                SERVER_URL + "activity/all",
                json={
                    "user_id": self.user.id,
                }
                if self.user
                else {},
                timeout=10,
            )
            if response.ok:
                data = response.json()
                activities = data.get("activities", [])
                self.populate_activities_table(activities)
        except Exception as e:
            print(f"Error loading activities: {e}")

    def populate_activities_table(self, activities):
        self.activities_table.setRowCount(len(activities))
        if not activities:
            self.activities_table.setRowCount(1)
            item = QTableWidgetItem("No activities available")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activities_table.setItem(0, 0, item)
            self.activities_table.setSpan(0, 0, 1, 4)
            return

        type_names = {0: "Academic", 1: "Cultural", 2: "Sports"}

        for i, activity in enumerate(activities):
            name = activity.get("name", "Unknown")
            activity_type = activity.get("type", 0)
            activity_id = activity.get("id")

            self.activities_table.setItem(i, 0, QTableWidgetItem(name))
            self.activities_table.setItem(
                i, 1, QTableWidgetItem(type_names.get(activity_type, "Unknown"))
            )

            try:
                members_response = requests.get(
                    SERVER_URL + f"activity/{activity_id}/members", timeout=10
                )
                if members_response.ok:
                    members_data = members_response.json()
                    member_count = len(members_data.get("members", []))
                    self.activities_table.setItem(
                        i, 2, QTableWidgetItem(str(member_count))
                    )
            except:
                self.activities_table.setItem(i, 2, QTableWidgetItem("0"))

            manage_btn = QPushButton("Manage")
            manage_btn.setStyleSheet(STYLES["button"])
            manage_btn.clicked.connect(
                lambda _: self.open_activity_details(activity_id)
            )
            self.activities_table.setCellWidget(i, 3, manage_btn)

    def open_activity_details(self, activity_id):
        parent_tab = self.parent()
        if self.on_open_activity_details:
            self.on_open_activity_details(activity_id)
