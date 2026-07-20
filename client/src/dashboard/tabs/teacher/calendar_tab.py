from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QDialog,
    QLineEdit,
    QTextEdit,
    QDateTimeEdit,
    QMessageBox,
    QCalendarWidget,
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
import requests
from theming.theme import theme
from constants import SERVER_URL


class CalendarTab(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_activity_id = None
        self.events = []
        self.setup_ui()

    def set_activity_id(self, activity_id):
        self.current_activity_id = activity_id
        self.load_calendar_data()

    def load_calendar_data(self):
        if not self.current_activity_id:
            self.show_no_activity()
            return

        try:
            response = requests.get(
                SERVER_URL + f"calendar/activity/{self.current_activity_id}",
                timeout=10,
            )

            if response.ok:
                data = response.json()
                calendar = data.get("calendar")
                events = data.get("events", [])
                self.events = events
                self.display_calendar(calendar, events)
            else:
                self.show_create_calendar_button()

        except Exception as e:
            print(f"Error loading calendar: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load calendar: {e}")

    def setup_ui(self):
        layout = QVBoxLayout(self)

        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """
        )

        main_layout = QHBoxLayout()

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
        self.calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)

        main_layout.addWidget(calendar_frame, 1)

        events_frame = QFrame()
        events_frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """
        )
        events_layout = QVBoxLayout(events_frame)

        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.setStyleSheet(
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
        self.add_event_button.clicked.connect(self.open_add_event_dialog)
        events_layout.addWidget(self.add_event_button)

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

        self.content_container = QFrame()
        self.content_container.setStyleSheet(
            f"""
            background: {theme.background.name()};
        """
        )
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setSpacing(15)

        scroll_area.setWidget(self.content_container)
        events_layout.addWidget(scroll_area)

        main_layout.addWidget(events_frame, 1)

        layout.addLayout(main_layout)

    def show_no_activity(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        no_activity_label = QLabel("No activity selected")
        no_activity_label.setStyleSheet(
            f"""
            font-size: 14px;
            color: {theme.text.name()};
            padding: 20px;
        """
        )
        no_activity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(no_activity_label)

    def show_create_calendar_button(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        create_button = QPushButton("Create Activity Calendar")
        create_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {theme.secondary.name()};
            }}
        """
        )
        create_button.clicked.connect(self.create_calendar)
        create_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(create_button)

    def create_calendar(self):
        if not self.current_activity_id:
            return

        try:
            response = requests.post(
                SERVER_URL + "calendar/activity",
                json={"activity_id": self.current_activity_id},
                timeout=10,
            )

            if response.ok:
                self.load_calendar_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to create calendar")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create calendar: {e}")

    def display_calendar(self, calendar, events):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if calendar:
            self.update_calendar_display()

        if not events:
            no_events_label = QLabel("No events scheduled")
            no_events_label.setStyleSheet(
                f"""
                font-size: 14px;
                color: {theme.text.name()};
                padding: 20px;
            """
            )
            no_events_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_events_label)
            return

        for event in events:
            event_frame = self.create_event_card(event)
            self.content_layout.addWidget(event_frame)

    def update_calendar_display(self):
        for event in self.events:
            try:
                start_time = datetime.fromisoformat(event.get("start_time"))
                date = QDate(start_time.year, start_time.month, start_time.day)
                self.calendar.setDateTextFormat(date, Qt.TextFormat.RichText)
            except:
                pass

    def on_date_selected(self, date):
        self.update_events_list(date)

    def update_events_list(self, date):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
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
            self.content_layout.addWidget(no_events_label)
            return

        for event in day_events:
            event_frame = self.create_event_card(event)
            self.content_layout.addWidget(event_frame)

    def create_event_card(self, event):
        frame = QFrame()
        frame.setStyleSheet(
            f"""
            background: {theme.background_alternative.name()};
            border-radius: 8px;
            padding: 12px;
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
                f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}"
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

        button_layout = QHBoxLayout()

        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {theme.secondary.name()};
            }}
        """
        )
        edit_button.clicked.connect(lambda: self.edit_event(event.get("id")))
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {theme.danger.name()};
                color: {theme.background.name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: #ff6b6b;
            }}
        """
        )
        delete_button.clicked.connect(lambda: self.delete_event(event.get("id")))
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        return frame

    def open_add_event_dialog(self):
        dialog = ActivityEventDialog(self.current_activity_id, self)
        dialog.exec()
        if dialog.result():
            self.load_calendar_data()

    def edit_event(self, event_id):
        dialog = ActivityEventDialog(self.current_activity_id, self, event_id)
        dialog.exec()
        if dialog.result():
            self.load_calendar_data()

    def delete_event(self, event_id):
        reply = QMessageBox.question(
            self,
            "Delete Event",
            "Are you sure you want to delete this event?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete(
                    SERVER_URL + f"calendar/event/{event_id}",
                    timeout=10,
                )

                if response.ok:
                    self.load_calendar_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete event")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete event: {e}")


class ActivityEventDialog(QDialog):
    def __init__(self, activity_id, parent=None, event_id=None):
        super().__init__(parent)
        self.activity_id = activity_id
        self.event_id = event_id
        self.setWindowTitle("Add Event" if event_id is None else "Edit Event")
        self.setup_ui()
        if event_id:
            self.load_event_data()

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

    def load_event_data(self):
        try:
            response = requests.get(
                SERVER_URL + f"calendar/activity/{self.activity_id}",
                timeout=10,
            )

            if response.ok:
                data = response.json()
                events = data.get("events", [])
                for event in events:
                    if event.get("id") == self.event_id:
                        self.title_input.setText(event.get("title", ""))
                        self.description_input.setPlainText(
                            event.get("description", "")
                        )
                        self.location_input.setText(event.get("location", ""))
                        try:
                            start_dt = datetime.fromisoformat(event.get("start_time"))
                            end_dt = datetime.fromisoformat(event.get("end_time"))
                            self.start_time.setDateTime(start_dt)
                            self.end_time.setDateTime(end_dt)
                        except:
                            pass
                        break

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load event: {e}")

    def save_event(self):
        if not self.activity_id:
            return

        try:
            response = requests.get(
                SERVER_URL + f"calendar/activity/{self.activity_id}",
                timeout=10,
            )

            if not response.ok:
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.warning(self, "Error", "Failed to get calendar")
                return

            data = response.json()
            calendar = data.get("calendar")

            if not calendar:
                create_response = requests.post(
                    SERVER_URL + "calendar/activity",
                    json={"activity_id": self.activity_id},
                    timeout=10,
                )

                if create_response.ok:
                    response = requests.get(
                        SERVER_URL + f"calendar/activity/{self.activity_id}",
                        timeout=10,
                    )

                    if not response.ok:
                        QMessageBox.warning(self, "Error", "Failed to create calendar")
                        return

                    data = response.json()
                    calendar = data.get("calendar")
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

            if self.event_id:
                response = requests.put(
                    SERVER_URL + f"calendar/event/{self.event_id}",
                    json=event_data,
                    timeout=10,
                )
            else:
                response = requests.post(
                    SERVER_URL + "calendar/event",
                    json=event_data,
                    timeout=10,
                )

            if response.ok:
                response_data = response.json()
                event_id = response_data.get("event_id")

                if event_id:
                    try:
                        requests.post(
                            SERVER_URL + f"calendar/sync/event/{event_id}",
                            json={},
                            timeout=10,
                        )
                    except:
                        pass
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to save event")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save event: {e}")
