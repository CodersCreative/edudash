from dataclasses import dataclass, field
from PySide6.QtGui import QColor, QFont


@dataclass
class Font:
    small: QFont
    default: QFont
    sub_heading: QFont
    heading: QFont
    large: QFont
    extra_large: QFont
    gigantic: QFont


def get_default_font() -> Font:
    return Font(
        small=QFont("Roboto", pointSize=12),
        default=QFont("Roboto", pointSize=14, weight=QFont.Weight.Bold),
        sub_heading=QFont("Roboto", pointSize=18, weight=QFont.Weight.Bold),
        heading=QFont("Roboto", pointSize=22, weight=QFont.Weight.Bold),
        large=QFont("Roboto", pointSize=36, weight=QFont.Weight.Bold),
        extra_large=QFont("Roboto", pointSize=64, weight=QFont.Weight.Bold),
        gigantic=QFont("Roboto", pointSize=120, weight=QFont.Weight.Bold),
    )


font = get_default_font()


def get_current_font() -> Font:
    return font
