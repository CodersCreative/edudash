from PySide6.QtWidgets import (
    QVBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
)
import requests
import routes
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL


class CreateTab(QFrame):
    def __init__(self, parent=None, on_load_activites=None):
        super().__init__(parent)
        self.user = None
        if routes.get_user:
            self.user = routes.get_user()
        self.on_load_activities = on_load_activites
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form_frame = QFrame()
        form_frame.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 10px; padding: 20px;"
        )
        form_layout = QVBoxLayout(form_frame)

        name_label = QLabel("Name:")
        name_label.setStyleSheet(f"color: {theme.text.name()};")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tennis")
        self.name_input.setStyleSheet(STYLES["textBox"])
        form_layout.addWidget(self.name_input)

        type_label = QLabel("Type:")
        type_label.setStyleSheet(f"color: {theme.text.name()};")
        form_layout.addWidget(type_label)

        self.type_input = QComboBox()
        self.type_input.addItems(["Academic", "Sports", "Cultural"])
        self.type_input.setStyleSheet(STYLES["textBox"])
        form_layout.addWidget(self.type_input)

        desc_label = QLabel("Description:")
        desc_label.setStyleSheet(f"color: {theme.text.name()};")
        form_layout.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Describe the activity...")
        self.desc_input.setStyleSheet(STYLES["textBox"])
        self.desc_input.setMaximumHeight(100)
        form_layout.addWidget(self.desc_input)

        create_btn = QPushButton("Create Activity")
        create_btn.setStyleSheet(STYLES["mainbutton"])
        create_btn.clicked.connect(self.create_activity)
        form_layout.addWidget(create_btn)

        layout.addWidget(form_frame)
        layout.addStretch()

    def create_activity(self):
        if not self.user:
            QMessageBox.warning(
                self, "Error", "You must be logged in to create activities."
            )
            return

        name = self.name_input.text().strip()
        activity_type = self.type_input.currentText()
        description = self.desc_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Error", "Activity name is required.")
            return

        type_map = {"Academic": 0, "Sports": 2, "Cultural": 1}
        activity_type_int = type_map.get(activity_type, 0)

        try:
            response = requests.post(
                SERVER_URL + "activity",
                json={
                    "name": name,
                    "description": description,
                    "type": activity_type_int,
                    "teacher_id": self.user.id,
                },
                timeout=10,
            )
            if response.ok:
                QMessageBox.information(
                    self, "Success", "Activity created successfully!"
                )
                self.name_input.clear()
                self.desc_input.clear()
                if self.on_load_activities:
                    self.on_load_activities()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    response.json().get("message", "Failed to create activity"),
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create activity: {e}")
