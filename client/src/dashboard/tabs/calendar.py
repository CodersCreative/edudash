from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QCalendarWidget,
    QPushButton,
    QScrollArea,
    QDialog,
    QLineEdit,
    QTextEdit,
    QDateTimeEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
import requests
from routes import User
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL


class CalendarTab(BaseTab):
    def __init__(self, user: User | None = None):
        super().__init__()
        self.user = user
        self.events = []
        self.setup_ui()
        self.load_calendar_data()

    def load_calendar_data(self):
        if not self.user:
            return

        try:
            response = requests.get(
                SERVER_URL + "calendar/personal",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if response.ok:
                data = response.json()
                self.events = data.get("events", [])
                self.update_calendar_display()
            else:
                self.create_personal_calendar()

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Error", f"Failed to load calendar: {e}")

    def create_personal_calendar(self):
        if not self.user:
            return

        try:
            response = requests.post(
                SERVER_URL + "calendar/personal",
                json={
                    "user_id": self.user.id,
                    "name": f"{self.user.username}'s Calendar",
                    "description": "Personal calendar",
                },
                timeout=10,
            )

            if response.ok:
                self.load_calendar_data()

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Error", f"Failed to create calendar: {e}")

    def setup_ui(self):
        layout = QHBoxLayout(self)

        calendar_frame = QFrame()
        calendar_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 20px;
        """
        )
        calendar_layout = QVBoxLayout(calendar_frame)

        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet(
            f"""
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
        """
        )
        self.calendar.clicked.connect(self.update_events_list)
        calendar_layout.addWidget(self.calendar)

        layout.addWidget(calendar_frame, 1)

        events_frame = QFrame()
        events_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """
        )
        events_layout = QVBoxLayout(events_frame)

        add_event_button = QPushButton("Add Event")
        add_event_button.setStyleSheet(
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
        add_event_button.clicked.connect(self.open_add_event_dialog)
        events_layout.addWidget(add_event_button)

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

        self.events_container = QFrame()
        self.events_container.setStyleSheet(
            f"""
            background: {theme.background.name()};
        """
        )
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setSpacing(10)

        scroll_area.setWidget(self.events_container)
        events_layout.addWidget(scroll_area)

        layout.addWidget(events_frame, 1)

    def update_calendar_display(self):
        for event in self.events:
            try:
                start_time = datetime.fromisoformat(event.get("start_time"))
                date = QDate(start_time.year, start_time.month, start_time.day)
                self.calendar.setDateTextFormat(date, Qt.TextFormat.RichText)
            except:
                pass

    def update_events_list(self, date):
        while self.events_layout.count():
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        selected_date = date.toPython()
        day_events = [
            event
            for event in self.events
            if datetime.fromisoformat(event.get("start_time")).date() == selected_date
        ]

        if not day_events:
            no_events_label = QLabel("No events on this day")
            no_events_label.setStyleSheet(
                f"""
                font-size: 14px;
                color: {theme.text.name()};
                padding: 20px;
            """
            )
            no_events_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.events_layout.addWidget(no_events_label)
            return

        for event in day_events:
            event_frame = self.create_event_card(event)
            self.events_layout.addWidget(event_frame)

    def create_event_card(self, event):
        frame = QFrame()
        frame.setStyleSheet(
            f"""
            background: {theme.background.name()};
            border-radius: 8px;
            padding: 12px;
            border: 1px solid {theme.background_alternative.name()};
        """
        )
        layout = QVBoxLayout(frame)

        title = QLabel(event.get("title", "Untitled Event"))
        title.setStyleSheet(
            f"""
            font-size: 14px;
            font-weight: bold;
            color: {theme.text.name()};
        """
        )
        layout.addWidget(title)

        try:
            start_time = datetime.fromisoformat(event.get("start_time"))
            end_time = datetime.fromisoformat(event.get("end_time"))
            time_label = QLabel(
                f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
            )
            time_label.setStyleSheet(
                f"""
                font-size: 12px;
                color: {theme.primary.name()};
            """
            )
            layout.addWidget(time_label)
        except:
            pass

        location = event.get("location")
        if location:
            location_label = QLabel(f"📍 {location}")
            location_label.setStyleSheet(
                f"""
                font-size: 11px;
                color: {theme.text.name()};
            """
            )
            layout.addWidget(location_label)

        description = event.get("description")
        if description:
            desc_label = QLabel(
                description[:100] + "..." if len(description) > 100 else description
            )
            desc_label.setStyleSheet(
                f"""
                font-size: 11px;
                color: {theme.text.name()};
            """
            )
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        is_synced = event.get("is_synced", False)
        if is_synced:
            activity_name = event.get("activity_name")
            if activity_name:
                synced_label = QLabel(f"From {activity_name}")
            else:
                synced_label = QLabel("From an activity")
            synced_label.setStyleSheet(
                f"""
                font-size: 10px;
                color: {theme.secondary.name()};
            """
            )
            layout.addWidget(synced_label)

        return frame

    def open_add_event_dialog(self):
        dialog = EventDialog(self.user, self)
        dialog.exec()
        if dialog.result():
            self.load_calendar_data()


class EventDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Add Event")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title_input = QLineEdit()
        title_input.setPlaceholderText("Event title")
        self.title_input = title_input
        layout.addWidget(title_input)

        description_input = QTextEdit()
        description_input.setPlaceholderText("Event description")
        description_input.setMaximumHeight(100)
        self.description_input = description_input
        layout.addWidget(description_input)

        location_input = QLineEdit()
        location_input.setPlaceholderText("Location")
        self.location_input = location_input
        layout.addWidget(location_input)

        time_layout = QHBoxLayout()

        start_time = QDateTimeEdit()
        start_time.setDateTime(datetime.now())
        start_time.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_time = start_time
        time_layout.addWidget(start_time)

        end_time = QDateTimeEdit()
        end_time.setDateTime(datetime.now())
        end_time.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_time = end_time
        time_layout.addWidget(end_time)

        layout.addLayout(time_layout)

        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_event)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def save_event(self):
        if not self.user:
            return

        try:
            response = requests.get(
                SERVER_URL + "calendar/personal",
                json={"user_id": self.user.id},
                timeout=10,
            )

            if not response.ok:
                QMessageBox.warning(self, "Error", "Failed to get calendar")
                return

            data = response.json()
            calendar = data.get("calendar")

            if not calendar:
                create_response = requests.post(
                    SERVER_URL + "calendar/personal",
                    json={
                        "user_id": self.user.id,
                        "name": f"{self.user.username}'s Calendar",
                        "description": "Personal calendar",
                    },
                    timeout=10,
                )

                if create_response.ok:
                    response = requests.get(
                        SERVER_URL + "calendar/personal",
                        json={"user_id": self.user.id},
                        timeout=10,
                    )
                    if response.ok:
                        data = response.json()
                        calendar = data.get("calendar")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to create calendar")
                        return
                else:
                    QMessageBox.warning(self, "Error", "Failed to create calendar")
                    return

            event_data = {
                "calendar_id": calendar.get("id"),
                "title": self.title_input.text(),
                "description": self.description_input.toPlainText(),
                "location": self.location_input.text(),
                "start_time": self.start_time.dateTime().toString(
                    "yyyy-MM-ddTHH:mm:ss"
                ),
                "end_time": self.end_time.dateTime().toString("yyyy-MM-ddTHH:mm:ss"),
            }

            response = requests.post(
                SERVER_URL + "calendar/event",
                json=event_data,
                timeout=10,
            )

            if response.ok:
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to create event")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save event: {e}")
