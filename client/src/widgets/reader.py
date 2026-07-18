from pathlib import Path
import zipfile

from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextBrowser,
    QLabel,
    QStackedWidget,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
)

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView
except Exception:
    QPdfDocument = None
    QPdfView = None

try:
    import markdown as md
except Exception:
    md = None

try:
    from ebooklib import epub
    from bs4 import BeautifulSoup
except Exception:
    epub = None
    BeautifulSoup = None
import requests
from constants import SERVER_URL

def get_book_progress(book_id: int, user_id: int) -> dict:
    response = requests.get(
        SERVER_URL + f"book/{book_id}/progress",
        params={"user_id": user_id},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def set_book_progress(book_id: int, user_id: int, page: int = 0, scroll: int = 0) -> None:
    response = requests.post(
        SERVER_URL + f"book/{book_id}/progress",
        json={"user_id": user_id, "page": page, "scroll": scroll},
        timeout=10,
    )
    response.raise_for_status()

class BookReaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path: Path | None = None
        self.book_id: int | None = None
        self.user_id: int | None = None
        self.progress = {"page": 0, "scroll": 0}
        self.pending_pdf_restore = False
        self.pending_restore_timer = QTimer(self)
        self.pending_restore_timer.setSingleShot(True)
        self.pending_restore_timer.timeout.connect(self.try_restore_pdf_page)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.empty = QLabel("Pick a book to start reading.")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text = QTextBrowser()
        self.text.setOpenExternalLinks(True)
        self.text.verticalScrollBar().valueChanged.connect(self.save_text_scroll)
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.text)

        self.controls = QWidget()
        control_layout = QHBoxLayout(self.controls)
        control_layout.setContentsMargins(0, 0, 0, 0)
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page 0 / 0")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.valueChanged.connect(self.jump_to_page_from_spin)
        self.prev_btn.clicked.connect(self.previous_page)
        self.next_btn.clicked.connect(self.next_page)
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.page_label, 1)
        control_layout.addWidget(self.page_spin)
        control_layout.addWidget(self.next_btn)
        self.stack.addWidget(self.controls)

        if QPdfDocument and QPdfView:
            self.pdf_doc = QPdfDocument(self)
            self.pdf_view = QPdfView()
            self.pdf_view.setDocument(self.pdf_doc)
            self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
            self.pdf_view.pageNavigator().currentPageChanged.connect(self.on_pdf_page_changed)
            self.pdf_doc.statusChanged.connect(self.on_pdf_status_changed)
            self.pdf_doc.pageCountChanged.connect(self.on_pdf_page_count_changed)
            self.stack.addWidget(self.pdf_view)
        else:
            self.pdf_doc = None
            self.pdf_view = None

        self.layout.addWidget(self.stack)
        self.set_controls_visible(False)

    def open_file(self, path: str | Path, book_id: int | None = None, user_id: int | None = None):
        self.current_path = Path(path)
        self.book_id = book_id
        self.user_id = user_id
        self.progress = {"page": 0, "scroll": 0}
        self.pending_pdf_restore = False
        self.load_progress()

        suffix = self.current_path.suffix.lower().lstrip(".")
        if suffix in {"md", "markdown"}:
            self.show_markdown(self.current_path)
        elif suffix == "pdf":
            self.show_pdf(self.current_path)
        elif suffix == "epub":
            self.show_epub(self.current_path)
        else:
            self.text.setPlainText(self.current_path.read_text(errors="ignore"))
            self.stack.setCurrentWidget(self.text)
            self.set_controls_visible(False)

    def show_markdown(self, path: Path):
        text = path.read_text(encoding="utf-8", errors="ignore")
        html = md.markdown(text, extensions=["fenced_code", "tables"]) if md else text
        self.text.setHtml(html)
        self.stack.setCurrentWidget(self.text)
        self.set_controls_visible(False)
        self.restore_text_scroll()

    def show_pdf(self, path: Path):
        if self.pdf_doc and self.pdf_view:
            self.pending_pdf_restore = True
            self.pdf_doc.load(str(path))
            self.stack.setCurrentWidget(self.pdf_view)
            self.set_controls_visible(True)
            self.pending_restore_timer.start(25)
            return
        self.text.setPlainText("PDF support requires QtPdf.")
        self.stack.setCurrentWidget(self.text)
        self.set_controls_visible(False)

    def show_epub(self, path: Path):
        if epub and BeautifulSoup:
            book = epub.read_epub(str(path))
            fragments = []
            for item in book.get_items():
                if item.get_type() == epub.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    fragments.append(soup.get_text("\n", strip=True))
            self.text.setPlainText("\n\n".join(fragments))
        else:
            with zipfile.ZipFile(path) as archive:
                names = [n for n in archive.namelist() if n.endswith((".xhtml", ".html", ".htm"))]
                snippets = []
                for name in names[:20]:
                    snippets.append(archive.read(name).decode("utf-8", errors="ignore"))
                self.text.setPlainText("\n\n".join(snippets))
        self.stack.setCurrentWidget(self.text)
        self.set_controls_visible(False)
        self.restore_text_scroll()

    def set_controls_visible(self, visible: bool):
        self.controls.setVisible(visible)

    def load_progress(self):
        if self.book_id is None or self.user_id is None:
            return
        try:
            self.progress = get_book_progress(self.book_id, self.user_id)
        except Exception:
            self.progress = {"page": 0, "scroll": 0}

    def save_progress(self, page: int | None = None, scroll: int | None = None):
        if self.book_id is None or self.user_id is None:
            return
        if page is not None:
            self.progress["page"] = page
        if scroll is not None:
            self.progress["scroll"] = scroll
        try:
            set_book_progress(
                self.book_id,
                self.user_id,
                self.progress.get("page", 0),
                self.progress.get("scroll", 0),
            )
        except Exception:
            pass

    def restore_pdf_page(self):
        if not self.pdf_doc or not self.pdf_view:
            return
        if self.pdf_doc.pageCount() <= 0:
            return
        page = max(0, min(int(self.progress.get("page", 0) or 0), self.pdf_doc.pageCount() - 1))
        self.pdf_view.pageNavigator().jump(page, QPointF(0, 0))
        self.page_spin.blockSignals(True)
        self.page_spin.setMaximum(max(1, self.pdf_doc.pageCount()))
        self.page_spin.setValue(page + 1)
        self.page_spin.blockSignals(False)
        self.page_label.setText(f"Page {page + 1} / {self.pdf_doc.pageCount()}")
        self.pending_pdf_restore = False

    def try_restore_pdf_page(self):
        if self.pending_pdf_restore and self.pdf_doc and self.pdf_doc.pageCount() > 0:
            self.restore_pdf_page()
            self.update_pdf_controls()

    def restore_text_scroll(self):
        self.text.verticalScrollBar().setValue(int(self.progress.get("scroll", 0) or 0))

    def save_text_scroll(self, value: int):
        if self.stack.currentWidget() == self.text:
            self.save_progress(scroll=value)

    def on_pdf_page_changed(self, page: int):
        if self.pdf_doc:
            self.page_label.setText(f"Page {page + 1} / {self.pdf_doc.pageCount()}")
            self.page_spin.blockSignals(True)
            self.page_spin.setMaximum(max(1, self.pdf_doc.pageCount()))
            self.page_spin.setValue(page + 1)
            self.page_spin.blockSignals(False)
        self.save_progress(page=page)

    def on_pdf_status_changed(self, *_):
        self.try_restore_pdf_page()

    def on_pdf_page_count_changed(self, *_):
        self.update_pdf_controls()
        self.try_restore_pdf_page()

    def update_pdf_controls(self):
        if self.pdf_doc and self.pdf_view:
            total = self.pdf_doc.pageCount()
            current = self.pdf_view.pageNavigator().currentPage()
            self.page_label.setText(f"Page {current + 1} / {total}")
            self.page_spin.blockSignals(True)
            self.page_spin.setMaximum(max(1, total))
            self.page_spin.setValue(current + 1)
            self.page_spin.blockSignals(False)

    def jump_to_page_from_spin(self, value: int):
        if self.pdf_view and self.pdf_doc and self.stack.currentWidget() == self.pdf_view:
            self.pdf_view.pageNavigator().jump(value - 1, QPointF(0, 0))

    def previous_page(self):
        if self.pdf_view and self.stack.currentWidget() == self.pdf_view:
            current = self.pdf_view.pageNavigator().currentPage()
            if current > 0:
                self.pdf_view.pageNavigator().jump(current - 1, QPointF(0, 0))

    def next_page(self):
        if self.pdf_view and self.pdf_doc and self.stack.currentWidget() == self.pdf_view:
            current = self.pdf_view.pageNavigator().currentPage()
            if current < self.pdf_doc.pageCount() - 1:
                self.pdf_view.pageNavigator().jump(current + 1, QPointF(0, 0))
