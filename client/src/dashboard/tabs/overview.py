from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSpinBox,
    QWidget,
)
from PySide6.QtCore import Qt, QTimer
from .base import BaseTab
from authentication.styles import STYLES
from theming.theme import theme


class OverviewTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_timer()
        self.setup_ui()

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 25 * 60
        self.timer_running = False
        self.editing_duration = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        horizontal_layout = QHBoxLayout()

        leaderboard_frame = QFrame()
        leaderboard_frame.setStyleSheet(f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """)
        leaderboard_layout = QVBoxLayout(leaderboard_frame)

        points_frame = QFrame()
        points_frame.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {theme.primary.name()}, stop:1 {theme.secondary.name()});
            border-radius: 15px;
            padding: 10px;
        """)
        points_layout = QVBoxLayout(points_frame)

        points_label = QLabel("345")
        points_label.setStyleSheet(f"""
            QLabel {{
                font-size: 64px;
                font-weight: bold;
                color: {theme.background.name()};
            }}
        """)
        points_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        points_layout.addWidget(points_label)
        leaderboard_layout.addWidget(points_frame)

        leaderboard_title = QLabel("Leaderboard")
        leaderboard_title.setStyleSheet(STYLES["titleText"])
        leaderboard_layout.addWidget(leaderboard_title)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setRowCount(5)
        table.setHorizontalHeaderLabels(["Rank", "Student", "Form", "Points"])
        table.setStyleSheet(f"""
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
        """)

        students = [
            (1, "Lorem Ipsum", 520),
            (2, "Lorem Ipsum", 485),
            (3, "Lorem Ipsum", 470),
            (4, "Lorem Ipsum", 455),
            (5, "Lorem Ipsum", 440),
        ]

        for i, (rank, name, points) in enumerate(students):
            table.setItem(i, 0, QTableWidgetItem(str(rank)))
            table.setItem(i, 1, QTableWidgetItem(name))
            table.setItem(i, 3, QTableWidgetItem(str(points)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        leaderboard_layout.addWidget(table)

        timer_frame = QFrame()
        timer_frame.setStyleSheet(f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """)
        timer_layout = QVBoxLayout(timer_frame)

        self.timer_container = QWidget()
        timer_container_layout = QVBoxLayout(self.timer_container)
        timer_container_layout.setContentsMargins(0, 0, 0, 0)

        self.timer_label = QLabel("25:00")
        self.timer_label.setStyleSheet(f"""
            QLabel {{
                font-size: 96px;
                font-weight: bold;
                color: {theme.primary.name()};
            }}
            QLabel:hover {{
                text-decoration: underline;
            }}
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.mousePressEvent = self.start_editing_duration
        timer_container_layout.addWidget(self.timer_label)

        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 120)
        self.duration_spinbox.setValue(25)
        self.duration_spinbox.setStyleSheet(f"""
            QSpinBox {{
                font-size: 96px;
                font-weight: bold;
                color: {theme.primary.name()};
                background: {theme.background.name()};
                border: 2px solid {theme.primary.name()};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        self.duration_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_spinbox.editingFinished.connect(self.finish_editing_duration)
        self.duration_spinbox.hide()
        timer_container_layout.addWidget(self.duration_spinbox)

        timer_layout.addWidget(self.timer_container)

        controls_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet(STYLES["mainbutton"])
        self.start_btn.clicked.connect(self.start_timer)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setStyleSheet(STYLES["mainbutton"])
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet(STYLES["mainbutton"])
        self.reset_btn.clicked.connect(self.reset_timer)

        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.reset_btn)
        timer_layout.addLayout(controls_layout)

        timetable_frame = QFrame()
        timetable_frame.setStyleSheet(f"""
            background: {theme.background_alternative.name()};
            border-radius: 10px;
            padding: 15px;
        """)
        timetable_layout = QVBoxLayout(timetable_frame)

        timetable_title = QLabel("Timetable")
        timetable_title.setStyleSheet(STYLES["titleText"])
        timetable_layout.addWidget(timetable_title)

        timetable_table = QTableWidget()
        timetable_table.setColumnCount(7)
        timetable_table.setRowCount(10)
        timetable_table.setHorizontalHeaderLabels(
            ["Time", "Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6"]
        )
        timetable_table.setStyleSheet(f"""
            QTableWidget {{
                background: {theme.background.name()};
                color: {theme.text.name()};
                gridline-color: {theme.background_alternative.name()};
                border-radius: 5px;
                font-size: 10px;
            }}
            QHeaderView::section {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
                padding: 3px;
                border-radius: 3px;
                font-size: 10px;
            }}
        """)
        times = [
            "07:30",
            "08:10",
            "08:50",
            "09:30",
            "10:05",
            "10:45",
            "11:25",
            "12:05",
            "12:45",
            "13:20",
        ]
        for i, time in enumerate(times):
            timetable_table.setItem(i, 0, QTableWidgetItem(time))

        timetable_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        timetable_table.verticalHeader().setVisible(False)
        timetable_layout.addWidget(timetable_table)

        horizontal_layout.addWidget(leaderboard_frame, 1)
        horizontal_layout.addWidget(timer_frame, 1)
        horizontal_layout.addWidget(timetable_frame, 1)

        layout.addLayout(horizontal_layout)

    def start_editing_duration(self, event):
        if not self.timer_running and not self.editing_duration:
            self.editing_duration = True
            self.timer_label.hide()
            self.duration_spinbox.setValue(self.remaining_time // 60)
            self.duration_spinbox.show()
            self.duration_spinbox.setFocus()
            self.duration_spinbox.selectAll()

    def finish_editing_duration(self):
        if self.editing_duration:
            self.editing_duration = False
            self.remaining_time = self.duration_spinbox.value() * 60
            self.update_display()
            self.duration_spinbox.hide()
            self.timer_label.show()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer.start(1000)
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.timer_running = False
        self.remaining_time = self.duration_spinbox.value() * 60
        self.update_display()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.timer_running = False
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)

    def update_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
