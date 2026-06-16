from dataclasses import dataclass, field
from PySide6.QtGui import QColor, QFont, QPalette

@dataclass
class Theme:
    background : QColor
    background_alternative : QColor
    primary_dark : QColor
    primary : QColor
    secondary : QColor
    tertiary : QColor
    danger : QColor 
    text : QColor

def get_default_theme() -> Theme:
    return Theme(
        background=QColor("#11111b"),
        background_alternative=QColor("#1e1e2e"),
        primary_dark=QColor("#2c1f4b"),
        primary=QColor("#cba6f7"),
        secondary=QColor("#a6e3a1"),
        tertiary=QColor("#f9e2af"),
        danger=QColor("#f38ba8"),
        text=QColor("#efe9fc")
    );

theme : Theme = get_default_theme();

def get_palette_from_theme(theme : Theme) -> QPalette:
    palette = QPalette();

    palette.setColor(QPalette.ColorRole.Window, theme.background);
    palette.setColor(QPalette.ColorRole.Base, theme.background);
    palette.setColor(QPalette.ColorRole.AlternateBase, theme.background_alternative);
    palette.setColor(QPalette.ColorRole.Accent, theme.primary);
    palette.setColor(QPalette.ColorRole.Dark, theme.background);
    palette.setColor(QPalette.ColorRole.Mid, theme.background_alternative);
    palette.setColor(QPalette.ColorRole.Button, theme.background_alternative);
    palette.setColor(QPalette.ColorRole.ToolTipBase, theme.background_alternative);
    palette.setColor(QPalette.ColorRole.ToolTipText, theme.text);
    palette.setColor(QPalette.ColorRole.NoRole, theme.background);
    palette.setColor(QPalette.ColorRole.Light, theme.text);
    palette.setColor(QPalette.ColorRole.ButtonText, theme.text);
    palette.setColor(QPalette.ColorRole.WindowText, theme.text);
    palette.setColor(QPalette.ColorRole.BrightText, theme.text);
    palette.setColor(QPalette.ColorRole.HighlightedText, theme.background);
    palette.setColor(QPalette.ColorRole.Highlight, theme.primary);
    palette.setColor(QPalette.ColorRole.Text, theme.text);

    palette.setColor(QPalette.ColorRole.PlaceholderText, theme.text.darker(2));

    return palette;

def get_current_theme() -> Theme:
    return theme;
