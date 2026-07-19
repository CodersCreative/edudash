from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QMessageBox,
    QSpinBox,
)
from PySide6.QtCore import Qt
import requests
import routes
from authentication.styles import STYLES
from theming.theme import theme
from constants import SERVER_URL


class ManageTab(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        if routes.get_user:
            self.user = routes.get_user()
        self.current_activity_id = None
        self.current_members = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.details_tabs = QTabWidget()
        self.details_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {theme.background_alternative.name()};
                background: {theme.background.name()};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background: {theme.background_alternative.name()};
                color: {theme.text.name()};
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QTabBar::tab:selected {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
            }}
        """)

        self.members_panel = self.create_members_panel()
        self.rewards_panel = self.create_rewards_panel()
        self.punishments_panel = self.create_punishments_panel()

        self.details_tabs.addTab(self.members_panel, "Members")
        self.details_tabs.addTab(self.rewards_panel, "Rewards")
        self.details_tabs.addTab(self.punishments_panel, "Punishments")

        layout.addWidget(self.details_tabs)

    def set_activity_id(self, activity_id):
        self.current_activity_id = activity_id
        self.load_activity_details()

    def load_activity_details(self):
        if not self.current_activity_id:
            return
        self.load_activity_members()
        self.load_activity_rewards()
        self.load_activity_punishments()

    def create_members_panel(self):
        panel = QFrame()
        layout = QHBoxLayout(panel)

        members_frame = QFrame()
        members_frame.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 10px; padding: 15px;"
        )
        members_layout = QVBoxLayout(members_frame)

        self.members_table = QTableWidget()
        self.members_table.setColumnCount(3)
        self.members_table.setHorizontalHeaderLabels(["Username", "Role", "Actions"])
        self.members_table.setStyleSheet(f"""
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
        self.members_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.members_table.verticalHeader().setVisible(False)
        members_layout.addWidget(self.members_table)

        layout.addWidget(members_frame)
        layout.setStretchFactor(members_frame, 3)

        add_frame = QFrame()
        add_frame.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 10px; padding: 15px;"
        )
        add_layout = QVBoxLayout(add_frame)

        title = QLabel("Add")
        title.setStyleSheet(STYLES["titleText"])
        add_layout.addWidget(title)

        user_select_layout = QHBoxLayout()
        user_select_layout.addWidget(QLabel("Select User:"))

        self.user_combo = QComboBox()
        self.user_combo.setStyleSheet(STYLES["textBox"])
        user_select_layout.addWidget(self.user_combo, 1)

        add_layout.addLayout(user_select_layout)

        role_select_layout = QHBoxLayout()
        role_select_layout.addWidget(QLabel("Role:"))

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Member", "Vice Captain", "Captain"])
        self.role_combo.setStyleSheet(STYLES["textBox"])
        role_select_layout.addWidget(self.role_combo, 1)

        add_layout.addLayout(role_select_layout)

        add_btn = QPushButton("Add Member")
        add_btn.setStyleSheet(STYLES["mainbutton"])
        add_btn.clicked.connect(self.add_member)
        add_layout.addWidget(add_btn)

        layout.addWidget(add_frame)
        layout.setStretchFactor(add_frame, 1)

        return panel

    def create_rewards_panel(self):
        panel = QFrame()
        layout = QHBoxLayout(panel)

        reward_frame = QFrame()
        reward_frame.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 10px; padding: 15px;"
        )
        reward_layout = QVBoxLayout(reward_frame)

        title = QLabel("Reward")
        title.setStyleSheet(STYLES["titleText"])
        reward_layout.addWidget(title)

        member_select_layout = QHBoxLayout()
        member_select_layout.addWidget(QLabel("Select Member:"))

        self.reward_member_combo = QComboBox()
        self.reward_member_combo.setStyleSheet(STYLES["textBox"])
        member_select_layout.addWidget(self.reward_member_combo, 1)

        reward_layout.addLayout(member_select_layout)

        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("Points:"))

        self.reward_points_input = QSpinBox()
        self.reward_points_input.setRange(1, 1000)
        self.reward_points_input.setValue(10)
        self.reward_points_input.setStyleSheet(STYLES["textBox"])
        points_layout.addWidget(self.reward_points_input, 1)

        reward_layout.addLayout(points_layout)

        reason_layout = QHBoxLayout()
        reason_layout.addWidget(QLabel("Reason:"))

        self.reward_reason_input = QLineEdit()
        self.reward_reason_input.setPlaceholderText("Reason for reward")
        self.reward_reason_input.setStyleSheet(STYLES["textBox"])
        reason_layout.addWidget(self.reward_reason_input, 1)

        reward_layout.addLayout(reason_layout)

        give_reward_btn = QPushButton("Give Reward")
        give_reward_btn.setStyleSheet(STYLES["mainbutton"])
        give_reward_btn.clicked.connect(self.give_reward)
        reward_layout.addWidget(give_reward_btn)

        history_frame = QFrame()
        history_frame.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 10px; padding: 15px;"
        )
        history_layout = QVBoxLayout(history_frame)

        self.rewards_table = QTableWidget()
        self.rewards_table.setColumnCount(3)
        self.rewards_table.setHorizontalHeaderLabels(["Member", "Points", "Reason"])
        self.rewards_table.setStyleSheet(f"""
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
        self.rewards_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.rewards_table.verticalHeader().setVisible(False)
        history_layout.addWidget(self.rewards_table)

        layout.addWidget(history_frame)
        layout.setStretchFactor(history_frame, 3)

        layout.addWidget(reward_frame)
        layout.setStretchFactor(reward_frame, 1)

        return panel

    def create_punishments_panel(self):
        panel = QFrame()
        layout = QHBoxLayout(panel)

        punishment_frame = QFrame()
        punishment_frame.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 10px; padding: 15px;"
        )
        punishment_layout = QVBoxLayout(punishment_frame)

        title = QLabel("Punish")
        title.setStyleSheet(STYLES["titleText"])
        punishment_layout.addWidget(title)

        member_select_layout = QHBoxLayout()
        member_select_layout.addWidget(QLabel("Select Member:"))

        self.punishment_member_combo = QComboBox()
        self.punishment_member_combo.setStyleSheet(STYLES["textBox"])
        member_select_layout.addWidget(self.punishment_member_combo, 1)

        punishment_layout.addLayout(member_select_layout)

        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("Points:"))

        self.punishment_points_input = QSpinBox()
        self.punishment_points_input.setRange(1, 1000)
        self.punishment_points_input.setValue(10)
        self.punishment_points_input.setStyleSheet(STYLES["textBox"])
        points_layout.addWidget(self.punishment_points_input, 1)

        punishment_layout.addLayout(points_layout)

        reason_layout = QHBoxLayout()
        reason_layout.addWidget(QLabel("Reason:"))

        self.punishment_reason_input = QLineEdit()
        self.punishment_reason_input.setPlaceholderText("Reason for punishment")
        self.punishment_reason_input.setStyleSheet(STYLES["textBox"])
        reason_layout.addWidget(self.punishment_reason_input, 1)

        punishment_layout.addLayout(reason_layout)

        give_punishment_btn = QPushButton("Give Punishment")
        give_punishment_btn.setStyleSheet(STYLES["mainbutton"])
        give_punishment_btn.clicked.connect(self.give_punishment)
        punishment_layout.addWidget(give_punishment_btn)

        history_frame = QFrame()
        history_frame.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 10px; padding: 15px;"
        )
        history_layout = QVBoxLayout(history_frame)

        self.punishments_table = QTableWidget()
        self.punishments_table.setColumnCount(3)
        self.punishments_table.setHorizontalHeaderLabels(["Member", "Points", "Reason"])
        self.punishments_table.setStyleSheet(f"""
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
        self.punishments_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.punishments_table.verticalHeader().setVisible(False)
        history_layout.addWidget(self.punishments_table)

        layout.addWidget(history_frame)
        layout.setStretchFactor(history_frame, 3)

        layout.addWidget(punishment_frame)
        layout.setStretchFactor(punishment_frame, 1)

        return panel

    def load_activity_members(self):
        try:
            response = requests.get(
                SERVER_URL + f"activity/{self.current_activity_id}/members", timeout=10
            )
            if response.ok:
                data = response.json()
                self.current_members = data.get("members", [])
                self.populate_members_table()
                self.populate_member_combos()
        except Exception as e:
            print(f"Error loading members: {e}")

    def load_activity_rewards(self):
        try:
            response = requests.get(
                SERVER_URL + "rewards/history", json={"user_id": None}, timeout=10
            )
            if response.ok:
                data = response.json()
                rewards = data.get("history", [])
                member_ids = {m.get("user_id") for m in self.current_members}
                activity_rewards = [
                    r for r in rewards if r.get("user_id") in member_ids
                ]
                self.populate_rewards_table(activity_rewards)
        except Exception as e:
            print(f"Error loading rewards: {e}")

    def load_activity_punishments(self):
        try:
            response = requests.get(
                SERVER_URL + "punish/history", json={"user_id": None}, timeout=10
            )
            if response.ok:
                data = response.json()
                punishments = data.get("history", [])
                member_ids = {m.get("user_id") for m in self.current_members}
                activity_punishments = [
                    p for p in punishments if p.get("user_id") in member_ids
                ]
                self.populate_punishments_table(activity_punishments)
        except Exception as e:
            print(f"Error loading punishments: {e}")

    def populate_members_table(self):
        self.members_table.setRowCount(len(self.current_members))
        if not self.current_members:
            self.members_table.setRowCount(1)
            item = QTableWidgetItem("No members yet")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.members_table.setItem(0, 0, item)
            self.members_table.setSpan(0, 0, 1, 3)
            return

        role_names = {
            0: "Member",
            1: "Vice Captain",
            2: "Captain",
            3: "Teacher",
            4: "Admin",
        }

        for i, member in enumerate(self.current_members):
            username = member.get("username", "Unknown")
            role = member.get("role", 0)
            user_id = member.get("user_id")

            self.members_table.setItem(i, 0, QTableWidgetItem(username))
            self.members_table.setItem(
                i, 1, QTableWidgetItem(role_names.get(role, "Member"))
            )

            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet(STYLES["button"])
            remove_btn.clicked.connect(
                lambda checked, uid=user_id: self.remove_member(uid)
            )
            self.members_table.setCellWidget(i, 2, remove_btn)

    def populate_member_combos(self):
        self.user_combo.clear()
        self.reward_member_combo.clear()
        self.punishment_member_combo.clear()

        for member in self.current_members:
            username = member.get("username", "Unknown")
            user_id = member.get("user_id")

            self.user_combo.addItem(username, user_id)
            self.reward_member_combo.addItem(username, user_id)
            self.punishment_member_combo.addItem(username, user_id)

    def populate_rewards_table(self, rewards):
        self.rewards_table.setRowCount(len(rewards))
        if not rewards:
            self.rewards_table.setRowCount(1)
            item = QTableWidgetItem("No rewards given yet")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rewards_table.setItem(0, 0, item)
            self.rewards_table.setSpan(0, 0, 1, 3)
            return

        for i, reward in enumerate(rewards):
            user_id = reward.get("user_id")
            points = reward.get("points", 0)
            reason = reward.get("reason", "Unknown")

            username = "Unknown"
            for member in self.current_members:
                if member.get("user_id") == user_id:
                    username = member.get("username", "Unknown")
                    break

            self.rewards_table.setItem(i, 0, QTableWidgetItem(username))
            self.rewards_table.setItem(i, 1, QTableWidgetItem(f"+{points}"))
            self.rewards_table.setItem(i, 2, QTableWidgetItem(reason))

    def populate_punishments_table(self, punishments):
        self.punishments_table.setRowCount(len(punishments))
        if not punishments:
            self.punishments_table.setRowCount(1)
            item = QTableWidgetItem("No punishments given yet")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.punishments_table.setItem(0, 0, item)
            self.punishments_table.setSpan(0, 0, 1, 3)
            return

        for i, punishment in enumerate(punishments):
            user_id = punishment.get("user_id")
            points = punishment.get("points", 0)
            reason = punishment.get("reason", "Unknown")

            username = "Unknown"
            for member in self.current_members:
                if member.get("user_id") == user_id:
                    username = member.get("username", "Unknown")
                    break

            self.punishments_table.setItem(i, 0, QTableWidgetItem(username))
            self.punishments_table.setItem(i, 1, QTableWidgetItem(f"-{points}"))
            self.punishments_table.setItem(i, 2, QTableWidgetItem(reason))

    def add_member(self):
        if self.user_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No users available to add.")
            return

        user_id = self.user_combo.currentData()
        role_text = self.role_combo.currentText()
        role_map = {"Member": 0, "Vice Captain": 1, "Captain": 2}
        role = role_map.get(role_text, 0)

        try:
            response = requests.post(
                SERVER_URL + f"activity/{self.current_activity_id}/members",
                json={"user_id": user_id, "role": role},
                timeout=10,
            )
            if response.ok:
                QMessageBox.information(self, "Success", "Member added successfully!")
                self.load_activity_members()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    response.json().get("message", "Failed to add member"),
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add member: {e}")

    def remove_member(self, user_id):
        try:
            response = requests.delete(
                SERVER_URL + f"activity/{self.current_activity_id}/members/{user_id}",
                timeout=10,
            )
            if response.ok:
                QMessageBox.information(self, "Success", "Member removed successfully!")
                self.load_activity_members()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    response.json().get("message", "Failed to remove member"),
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to remove member: {e}")

    def give_reward(self):
        if self.reward_member_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No members available.")
            return

        user_id = self.reward_member_combo.currentData()
        points = self.reward_points_input.value()
        reason = self.reward_reason_input.text().strip()

        if not reason:
            QMessageBox.warning(self, "Error", "Reason is required.")
            return

        if not self.user:
            QMessageBox.warning(self, "Error", "Sign in to give reward.")
            return

        try:
            response = requests.post(
                SERVER_URL + "reward",
                json={
                    "user_id": user_id,
                    "teacher_id": self.user.id,
                    "points": points,
                    "reason": reason,
                    "activity_id": self.current_activity_id,
                },
                timeout=10,
            )
            if response.ok:
                QMessageBox.information(self, "Success", "Reward given successfully!")
                self.reward_reason_input.clear()
                self.load_activity_rewards()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    response.json().get("message", "Failed to give reward"),
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to give reward: {e}")

    def give_punishment(self):
        if self.punishment_member_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No members available.")
            return

        user_id = self.punishment_member_combo.currentData()
        points = self.punishment_points_input.value()
        reason = self.punishment_reason_input.text().strip()

        if not reason:
            QMessageBox.warning(self, "Error", "Reason is required.")
            return

        if not self.user:
            QMessageBox.warning(self, "Error", "Sign in to give punishment.")
            return

        try:
            response = requests.post(
                SERVER_URL + "punish",
                json={
                    "user_id": user_id,
                    "teacher_id": self.user.id,
                    "points": points,
                    "reason": reason,
                    "activity_id": self.current_activity_id,
                },
                timeout=10,
            )
            if response.ok:
                QMessageBox.information(
                    self, "Success", "Punishment given successfully!"
                )
                self.punishment_reason_input.clear()
                self.load_activity_punishments()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    response.json().get("message", "Failed to give punishment"),
                )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to give punishment: {e}")
