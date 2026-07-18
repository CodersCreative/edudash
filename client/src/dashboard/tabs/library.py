from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import os
import tempfile
import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import routes
from authentication.styles import STYLES
from constants import SERVER_URL
from theming.theme import theme
from widgets.reader import BookReaderWidget
from .base import BaseTab


@dataclass
class LibraryBook:
    id: int
    title: str
    author: str
    description: str | None
    file_type: str
    isbn13: str | None
    owner_id: int | None


def fetch_books(query: str = "", available_only: bool = False) -> list[LibraryBook]:
    response = requests.get(
        SERVER_URL + "book/all",
        params={"query": query, "available_only": str(available_only).lower()},
        timeout=10,
    )
    response.raise_for_status()
    return [LibraryBook(**book) for book in response.json().get("books", [])]


def borrow_book(book_id: int, user_id: int) -> requests.Response:
    return requests.post(
        SERVER_URL + f"book/{book_id}/borrow",
        json={"user_id": user_id},
        timeout=10,
    )


def return_book(book_id: int, user_id: int) -> requests.Response:
    return requests.post(
        SERVER_URL + f"book/{book_id}/return",
        json={"user_id": user_id},
        timeout=10,
    )


def add_book(
    user_id: int,
    file_path: str,
    title: str | None = None,
    description: str | None = None,    
    author: str | None = None,    
    isbn13: str | None = None,
    isbn10: str | None = None,    
) -> requests.Response:
    file_name = Path(file_path).name
    with open(file_path, "rb") as handle:
        files = {
            "json": (
                "json",
                json.dumps(
                    {
                        "user_id": user_id,
                        "title": title,
                        "description": description,
                        "author": author,
                        "isbn13": isbn13,
                        "isbn10": isbn10,
                    }
                ),
                "application/json",
            ),
            "file": (file_name, handle),
        }
        return requests.post(SERVER_URL + "book", files=files, timeout=20)


def download_book(user_id: int,book_id: int) -> Path:
    response = requests.get(SERVER_URL + f"book/{book_id}/download", json={
            "user_id": user_id,
        }, timeout=20)
    response.raise_for_status()
    suffix = response.headers.get("content-type", "").split("/")[-1]
    if "pdf" in suffix:
        ext = ".pdf"
    elif "epub" in suffix:
        ext = ".epub"
    else:
        ext = ".txt"
    fd, path = tempfile.mkstemp(prefix=f"book-{book_id}-", suffix=ext)
    with os.fdopen(fd, "wb") as handle:
        handle.write(response.content)
    return Path(path)


class LibraryBookCard(QFrame):
    def __init__(self, book, on_open, on_borrow, on_return, parent=None):
        super().__init__(parent)
        self.book = book
        self.on_open = on_open
        self.on_borrow = on_borrow
        self.on_return = on_return
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {theme.background_alternative.name()};
                border: 1px solid {theme.primary_dark.name()};
                border-radius: 14px;
            }}
            """
        )
        layout = QVBoxLayout(self)
        title = QLabel(book.title)
        title.setStyleSheet(STYLES["titleText"])
        author = QLabel(f"by {book.author}")
        author.setStyleSheet(f"color: {theme.primary.name()};")
        desc = QLabel(book.description or "No description available.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {theme.text.name()};")
        meta = QLabel(
            f"{book.file_type.upper()}  |  {'Available' if not book.owner_id else 'Checked out'}"
        )
        meta.setStyleSheet(f"color: {theme.secondary.name()};")

        actions = QHBoxLayout()

        if not book.owner_id:
            borrow_btn = QPushButton("Take Out")
            borrow_btn.setStyleSheet(STYLES["button"])
            borrow_btn.clicked.connect(lambda: self.on_borrow(book))
            actions.addWidget(borrow_btn)
        elif routes.get_user and routes.get_user() and book.owner_id == routes.get_user().id:
                open_btn = QPushButton("Read")
                open_btn.setStyleSheet(STYLES["mainbutton"])
                open_btn.clicked.connect(lambda: self.on_open(book))
                actions.addWidget(open_btn)            

                return_btn = QPushButton("Return")
                return_btn.setStyleSheet(STYLES["button"])
                return_btn.clicked.connect(lambda: self.on_return(book))
                actions.addWidget(return_btn)

        layout.addWidget(title)
        layout.addWidget(author)
        layout.addWidget(meta)
        layout.addWidget(desc)
        layout.addLayout(actions)


class FindTab(QWidget):
    def __init__(self, library):
        super().__init__()
        self.library = library
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search title, author, description, or format")
        self.search_input.setStyleSheet(STYLES["textBox"])
        self.search_input.textChanged.connect(self.library.refresh_books)
        self.available_only = QPushButton("Available only")
        self.available_only.setCheckable(True)
        self.available_only.setStyleSheet(STYLES["button"])
        self.available_only.toggled.connect(self.library.refresh_books)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(STYLES["mainbutton"])
        refresh_btn.clicked.connect(self.library.refresh_books)
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(self.available_only)
        search_row.addWidget(refresh_btn)
        root.addLayout(search_row)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setWidget(self.results_container)
        root.addWidget(self.results_area, 1)


class ImportTab(QWidget):
    def __init__(self, library):
        super().__init__()
        self.library = library
        self.setup_ui()

    def import_file(self):
        self.file.setText(self.library.pick_file())

    def add_book(self):
        self.library.add_book(False)

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        import_box = QFrame()
        import_box.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 16px; padding: 14px;"
        )
        layout = QVBoxLayout(import_box)
        self.import_title = QLineEdit()
        self.import_title.setPlaceholderText("Title")
        self.import_isbn13 = QLineEdit()
        self.import_isbn13.setPlaceholderText("ISBN-13")
        self.import_isbn10 = QLineEdit()
        self.import_isbn10.setPlaceholderText("ISBN-10")

        self.file = QLineEdit()
        self.file.setPlaceholderText("Upload a markdown, pdf, or epub file")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.import_file)
        import_btn = QPushButton("Import")
        import_btn.setStyleSheet(STYLES["mainbutton"])
        import_btn.clicked.connect(self.add_book)
        file_row = QHBoxLayout()
        file_row.addWidget(self.file, 1)
        file_row.addWidget(browse_btn)
        layout.addWidget(self.import_title)
        layout.addWidget(self.import_isbn13)
        layout.addWidget(self.import_isbn10)        
        layout.addLayout(file_row)
        layout.addWidget(import_btn)
        root.addWidget(import_box)


class ReadTab(QWidget):
    def __init__(self, library):
        super().__init__()
        self.library = library
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        self.reader_info = QLabel("Choose a book from Find or use the open action to load it here.")
        self.reader_info.setWordWrap(True)
        root.addWidget(self.reader_info)
        root.addWidget(self.library.reader, 1)


class SelfPublishTab(QWidget):
    def __init__(self, library):
        super().__init__()
        self.library = library
        self.setup_ui()

    def import_file(self):
        self.file.setText(self.library.pick_file())
        
    def add_book(self):
        self.library.add_book(True)

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        publish_box = QFrame()
        publish_box.setStyleSheet(
            f"background: {theme.background_alternative.name()}; border-radius: 16px; padding: 14px;"
        )
        publish_layout = QVBoxLayout(publish_box)
        self.publish_title = QLineEdit()
        self.publish_title.setPlaceholderText("Book title")
        self.publish_desc = QTextEdit()
        self.publish_desc.setPlaceholderText("Book description")
        self.publish_author = QLineEdit()
        self.publish_author.setPlaceholderText("Author name")
        if routes.get_user and routes.get_user():
            self.publish_author.setText(routes.get_user().username)
        self.file = QLineEdit()
        self.file.setPlaceholderText("Upload a markdown, pdf, or epub file")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.import_file)
        upload_btn = QPushButton("Publish")
        upload_btn.setStyleSheet(STYLES["mainbutton"])
        upload_btn.clicked.connect(self.add_book)
        file_row = QHBoxLayout()
        file_row.addWidget(self.file, 1)
        file_row.addWidget(browse_btn)
        publish_layout.addWidget(self.publish_title)
        publish_layout.addWidget(self.publish_author)
        publish_layout.addWidget(self.publish_desc)
        publish_layout.addLayout(file_row)
        publish_layout.addWidget(upload_btn)
        root.addWidget(publish_box)


class LibraryTab(BaseTab):
    def __init__(self):
        super().__init__()
        self.current_books: list[LibraryBook] = []
        self.selected_book = None
        self.local_temp_file: Path | None = None
        self.reader = BookReaderWidget()
        self.setup_ui()
        self.refresh_books()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {theme.background_alternative.name()};
                background: {theme.background.name()};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background: {theme.background_alternative.name()};
                color: {theme.text.name()};
                padding: 10px 18px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: {theme.primary.name()};
                color: {theme.background.name()};
            }}
            """
        )

        self.find_tab = FindTab(self)
        self.read_tab = ReadTab(self)
        self.import_tab = ImportTab(self)
        self.upload_tab = SelfPublishTab(self)
        self.tabs.addTab(self.find_tab, "Find")
        self.tabs.addTab(self.read_tab, "Read")
        self.tabs.addTab(self.import_tab, "Import")
        self.tabs.addTab(self.upload_tab, "Upload")
        root.addWidget(self.tabs, 1)

    def refresh_books(self, *_):
        try:
            self.current_books = fetch_books(
                self.find_tab.search_input.text().strip(),
                self.find_tab.available_only.isChecked(),
            )
        except Exception as exc:
            QMessageBox.warning(self, "Library", f"Could not load books: {exc}")
            self.current_books = []
        self.render_books()

    def render_books(self):
        while self.find_tab.results_layout.count():
            item = self.find_tab.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if not self.current_books:
            empty = QLabel("No books match this search.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.find_tab.results_layout.addWidget(empty)
            return
        for book in self.current_books:
            card = LibraryBookCard(book, self.open_book, self.borrow_selected, self.return_selected)
            self.find_tab.results_layout.addWidget(card)
        self.find_tab.results_layout.addStretch()

    def pick_file(self) -> str:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Book File",
            "",
            "Books (*.pdf *.epub *.md *.markdown)",
        )
        return path

    def open_book(self, book):
        user = routes.get_user() if routes.get_user else None
        if not user:
            QMessageBox.warning(self, "Library", "Please sign in to borrow books.")
            return
        
        try:
            path = download_book(book.id, user.id)
        except Exception as exc:
            QMessageBox.warning(self, "Reader", f"Could not open book: {exc}")
            return

        self.local_temp_file = path
        self.read_tab.reader_info.setText(f"{book.title} by {book.author}")
        self.reader.open_file(path, book.id, user.id)
        self.selected_book = book
        self.tabs.setCurrentWidget(self.read_tab)

    def borrow_selected(self, book):
        user = routes.get_user() if routes.get_user else None
        if not user:
            QMessageBox.warning(self, "Library", "Please sign in to borrow books.")
            return

        response = borrow_book(book.id, user.id)
        if response.ok:
            QMessageBox.information(self, "Library", "Book checked out.")
            self.refresh_books()
        else:
            QMessageBox.warning(self, "Library", response.json().get("error", "Could not borrow."))

    def return_selected(self, book):
        user = routes.get_user() if routes.get_user else None
        if not user:
            QMessageBox.warning(self, "Library", "Please sign in to return books.")
            return

        response = return_book(book.id, user.id)
        if response.ok:
            QMessageBox.information(self, "Library", "Book returned.")
            self.refresh_books()
        else:
            QMessageBox.warning(self, "Library", response.json().get("error", "Could not return."))

    def add_book(self, self_publish : bool):
        user = routes.get_user() if routes.get_user else None
        if not user:
            QMessageBox.warning(self, "Library", "Please sign in to self-publish books.")
            return
        
        file_path = self.upload_tab.file.text().strip() if self_publish else self.import_tab.file.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Library", "Choose a resource file first.")
            return

        if self_publish:
            response = add_book(
                user_id=user.id,
                title=self.upload_tab.publish_title.text().strip(),
                description=self.upload_tab.publish_desc.toPlainText().strip(),
                author=self.upload_tab.publish_author.text().strip() or routes.get_user().username,
                file_path=file_path,
            )
            if response.ok:
                QMessageBox.information(self, "Library", "Your book is now published.")
                self.upload_tab.publish_title.clear()
                self.upload_tab.publish_desc.clear()
                self.upload_tab.file.clear()
                self.refresh_books()
            else:
                QMessageBox.warning(self, "Library", response.json().get("error", "Could not publish."))
        else:
            response = add_book(
                user_id=user.id,
                title=self.import_tab.import_title.text().strip(),
                isbn13=self.import_tab.import_isbn13.text().strip(),
                isbn10=self.import_tab.import_isbn10.text().strip(),
                file_path=file_path,
            )
            if response.ok:
                QMessageBox.information(self, "Library", "Your book is now published.")

                self.import_tab.import_title.clear()
                self.import_tab.import_isbn13.clear()
                self.import_tab.import_isbn10.clear()
                self.import_tab.file.clear()
                self.refresh_books()
            else:
                QMessageBox.warning(self, "Library", response.json().get("error", "Could not publish."))   
