from PySide6.QtWidgets import QVBoxLayout, QTabWidget
from theming.theme import theme
from ..base import BaseTab
from .create_tab import CreateTab
from .activities_tab import ActivitiesTab
from .manage_tab import ManageTab


class TeacherTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
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

        self.create_tab = CreateTab(self, self.load_activities)
        self.activities_tab = ActivitiesTab(self, self.open_activity_details)
        self.manage_tab = ManageTab(self)

        self.tabs.addTab(self.create_tab, "Create")
        self.tabs.addTab(self.activities_tab, "All")
        self.tabs.addTab(self.manage_tab, "Manage")
        self.tabs.setTabEnabled(2, False)

        layout.addWidget(self.tabs)

    def load_activities(self):
        self.activities_tab.load_activities()

    def open_activity_details(self, activity_id):
        self.manage_tab.set_activity_id(activity_id)
        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentIndex(2)
