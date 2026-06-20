from dataclasses import dataclass
from PySide6.QtGui import QIcon
from PySide6.QtSvgWidgets import QSvgWidget

from utils import get_project_path


@dataclass
class Icons:
    cancel: QIcon
    account: QIcon
    book: QIcon
    comedy_mask: QIcon
    sports: QIcon
    delete: QIcon
    add: QIcon
    home_outline: QIcon
    x: QIcon


def get_path(name: str):
    return f"{get_project_path()}/src/assets/icons/" + name


def get_default_icons() -> Icons:
    return Icons(
        cancel=QIcon(get_path("cancel.svg")),
        account=QIcon(get_path("account.svg")),
        book=QIcon(get_path("book.svg")),
        comedy_mask=QIcon(get_path("comedy_mask.svg")),
        sports=QIcon(get_path("sports.svg")),
        delete=QIcon(get_path("delete.svg")),
        add=QIcon(get_path("add.svg")),
        home_outline=QIcon(get_path("home-outline.svg")),
        x=QIcon(get_path("x.svg")),
    )


icons: Icons = get_default_icons()


def get_icon(path: str, size=None) -> QSvgWidget:
    icon = QSvgWidget(get_path(path))
    if size is not None:
        icon.setFixedSize(size, size)
    icon.setStyleSheet("background: transparent; margin-right: 10px;")
    return icon
