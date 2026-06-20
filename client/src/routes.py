from typing import Callable, Optional

from PySide6.QtGui import QPalette

# Helpers
set_background_style: Optional[Callable[[Optional[str]], None]] = None
reset_palette: Optional[Callable[[], None]] = None
set_colour_role: Optional[Callable[[QPalette.ColorRole], None]] = None
set_user: Optional[Callable[[str, str], None]] = None
get_user: Optional[Callable[[], tuple[str, str]]] = None
# Routes
open_signup: Optional[Callable[[], None]] = None
open_login: Optional[Callable[[], None]] = None
open_dashboard: Optional[Callable[[], None]] = None
