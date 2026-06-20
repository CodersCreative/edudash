from PySide6.QtWidgets import (
    QVBoxLayout,
)
from .base import BaseTab


class TeacherTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addStretch()
