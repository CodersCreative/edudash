from dataclasses import dataclass
from typing import Callable

from PySide6.QtGui import QPalette


@dataclass
class User:
    username: str
    id: int
    role: int
    points: int


# Helpers
set_background_style: Callable[[str | None], None] | None = None
reset_palette: Callable[[], None] | None = None
set_colour_role: Callable[[QPalette.ColorRole], None] | None = None
set_user: Callable[[User], None] | None = None
get_user: Callable[[], User] | None = None
# Routes
open_signup: Callable[[], None] | None = None
open_login: Callable[[], None] | None = None
open_dashboard: Callable[[], None] | None = None
