from flask import json, request, jsonify, send_file
from sqlalchemy import select
from model_database import (
    Book,
    BookProgress,
    db,
)
from utils import (
    allowed_book_extension,
    get_book_details,
    normalize_book_extension,
    safe_book_filename,
    get_library_path,
)
from app import app


@app.route("/book", methods=["POST"])
def add_book():
    if "json" in request.files:
        data = json.load(request.files["json"])
    elif request.is_json:
        data = request.get_json()
    else:
        data = request.form

    owner_id = data.get("user_id")
    title = (data.get("title") or "").strip()
    isbn13 = (data.get("isbn13") or "").strip()
    isbn10 = (data.get("isbn10") or "").strip()
    description = data.get("description")
    author = data.get("author") or data.get("username")

    f = request.files.get("file")

    if author is None or description is None:
        if not title and not isbn13 and not isbn10:
            return jsonify({"error": "Provide a title or ISBN to import"}), 400

        book = get_book_details(title=title, isbn13=isbn13, isbn10=isbn10)

        if not book:
            return jsonify({"error": "Book unable to be found"}), 404

        if book:
            title = book.title or title
            authors = book.authors
            if authors and not author:
                author = authors[0]
            description = book.description or description
            isbn13 = isbn13 or book.ISBN_13

    author = author or "Unknown Author"

    if not title:
        return jsonify({"error": "Title is required"}), 400

    if f and f.filename:
        if not allowed_book_extension(f.filename):
            return jsonify(
                {"error": "Only markdown, pdf, and epub files are supported"}
            ), 400

        file_type = normalize_book_extension(f.filename)
        filename = safe_book_filename(title, author, f.filename)
        file_path = get_library_path() / filename
        f.save(file_path)
    else:
        return jsonify({"error": "Expected a file"}), 400

    new_book = Book(
        owner_id=owner_id,
        isbn13=isbn13,
        title=title,
        description=description,
        file=str(file_path),
        file_type=file_type,
        author=author,
        is_public=True,
    )
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Book added successfully", "book_id": new_book.id}), 201


@app.route("/book/all", methods=["GET"])
def list_books():
    query = request.args.get("query", "").strip().lower()
    available_only = request.args.get("available_only", "false").lower() == "true"
    books_query = db.session.scalars(select(Book)).all()

    results = []
    for book in books_query:
        if not book.is_public:
            continue
        haystack = " ".join(
            [
                book.title or "",
                book.author or "",
                book.description or "",
                book.file_type or "",
            ]
        ).lower()
        if query and query not in haystack:
            continue
        if available_only and not book.owner_id:
            continue
        results.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "file_type": book.file_type,
                "isbn13": book.isbn13,
                "owner_id": book.owner_id,
            }
        )

    return jsonify({"books": results}), 200


@app.route("/book/<int:book_id>/borrow", methods=["POST"])
def borrow_book(book_id: int):
    data = request.get_json()
    user_id = data.get("user_id")
    book = db.session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        return jsonify({"error": "Book not found"}), 404
    if book.owner_id == user_id:
        return jsonify({"error": "You already own this book"}), 409
    if book.owner_id is not None:
        return jsonify({"error": "Book is already borrowed"}), 409
    book.owner_id = user_id
    db.session.commit()
    return jsonify({"message": "Book borrowed"}), 200


@app.route("/book/<int:book_id>/return", methods=["POST"])
def return_book(book_id: int):
    data = request.get_json()
    user_id = data.get("user_id")
    book = db.session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        return jsonify({"error": "Book not found"}), 404
    if book.owner_id != user_id:
        return jsonify({"error": "You do not currently have this book"}), 403
    book.owner_id = None
    db.session.commit()
    return jsonify({"message": "Book returned"}), 200


@app.route("/book/<int:book_id>/download", methods=["GET"])
def download_book(book_id: int):
    data = request.args if request.args else request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    book = db.session.scalar(select(Book).where(Book.id == book_id))

    if not book:
        return jsonify({"error": "Book not found"}), 404
    if book.owner_id != user_id:
        return jsonify({"error": "You do not currently have this book"}), 403

    return send_file(book.file, as_attachment=False)


@app.route("/book/<int:book_id>/progress", methods=["GET"])
def get_book_progress(book_id: int):
    data = request.args if request.args else request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    progress = db.session.scalar(
        select(BookProgress).where(
            BookProgress.book_id == book_id,
            BookProgress.user_id == int(user_id),
        )
    )
    if not progress:
        return jsonify({"page": 0, "scroll": 0}), 200
    return jsonify({"page": progress.page, "scroll": progress.scroll}), 200


@app.route("/book/<int:book_id>/progress", methods=["POST"])
def set_book_progress(book_id: int):
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    page = int(data.get("page", 0) or 0)
    scroll = int(data.get("scroll", 0) or 0)
    progress = db.session.scalar(
        select(BookProgress).where(
            BookProgress.book_id == book_id,
            BookProgress.user_id == int(user_id),
        )
    )
    if not progress:
        progress = BookProgress(
            user_id=int(user_id), book_id=book_id, page=page, scroll=scroll
        )
        db.session.add(progress)
    else:
        progress.page = page
        progress.scroll = scroll
    db.session.commit()
    return jsonify({"message": "Progress saved"}), 200
