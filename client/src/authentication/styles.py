from theming.theme import theme

STYLES = {
    "titleText": f"""
        QLabel {{
            font-size: 36px;
            font-weight: bold;
           
            color: {theme.text.name()};
            qproperty-alignment: 'AlignCenter';
        }}
    """,

    "titleTextInverted": f"""
        QLabel {{
            font-size: 36px;
            font-weight: bold;
           
            color: {theme.background.name()};
            qproperty-alignment: 'AlignCenter';
        }}
    """,
    
    "normalText": f"""
        QLabel {{
           
            font-size: 16px;
            line-height: 28px;
            color: {theme.text.name()};
            qproperty-wordWrap: true;
            qproperty-alignment: 'AlignCenter';
        }}
    """,

    "normalTextInverted": f"""
        QLabel {{
           
            font-size: 16px;
            line-height: 28px;
            color: {theme.background.name()};
            qproperty-wordWrap: true;
            qproperty-alignment: 'AlignCenter';
        }}
    """,

    "button": f"""
        QPushButton {{
            font-size: 14px;
            width: 170px;
            background: transparent;
            color: {theme.background.name()};
            border-radius: 25px;
            border: 1px solid {theme.background.name()};
            padding: 15px;
        }}
        QPushButton:hover {{
            background-color: {theme.text.name()};
            color: {theme.background_alternative.name()};
        }}
        QPushButton:pressed {{
            background-color: {theme.text.name()};
            color: {theme.background_alternative.name()};
        }}
    """,

    "mainbutton": f"""
        QPushButton {{
            font-size: 14px;
            width: 200px;
            margin-top: 20px;
            background: {theme.primary.name()};
            color: {theme.background.name()};
            border-radius: 25px;
            border: 1px solid {theme.primary.name()};
            padding: 15px;
        }}
        QPushButton:hover {{
            background-color: {theme.primary.name()};
            color: {theme.text.name()};
        }}
        QPushButton:pressed {{
            background-color: {theme.primary.name()};
            color: {theme.text.name()};
        }}
    """,

    "buttonCircle": f"""
        QPushButton {{
            background: transparent;
            border: 1px solid {theme.background_alternative.name()};
            border-radius: 30px;
            padding: 15px;
            margin-right: 8px;
            margin-left: 8px;
        }}
        QPushButton:hover {{
            background-color: {theme.text.name()};
        }}
        QPushButton:pressed {{
            background-color: {theme.text.name()};
        }}
    """,

    "textHint": f"""
        QLabel {{
            font-size: 14px;
            color: {theme.text.name()};
            margin-left: 10px;
        }}
    """,

    "textBox": f"""
        QLineEdit, QPlainTextEdit {{
            font-size: 14px;
            color: {theme.text.name()};
            border: none;
            margin-left: 10px;
        }}
    """,

    "imgClose": """
        QLabel {
            width: 30px;
            height: 30px;
            margin-top: 13px;
            margin-right: 13px;
        }
        QLabel:hover {
            transform: scale(1.1); /* won't work in QSS, may need animation or event handler */
        }
    """
}
