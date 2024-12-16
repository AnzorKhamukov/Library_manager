from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import sessionmaker
from app.database import engine

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_author():
    response = client.post("/authors/", json={
        "first_name": "Лев",
        "last_name": "Толстой",
        "birth_date": "1828-09-09T00:00:00"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Лев"
    assert data["last_name"] == "Толстой"
    assert data["birth_date"] == "1828-09-09T00:00:00"


def test_list_authors():
    response = client.get("/authors/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_book():
    response = client.post("/books/", json={
        "title": "Война и мир",
        "description": "Роман Льва Толстого",
        "author_id": 1,
        "available_copies": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Война и мир"
    assert data["description"] == "Роман Льва Толстого"
    assert data["author_id"] == 1
    assert data["available_copies"] == 10


def test_list_books():
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_borrow_success():
    response = client.post("/borrows/", json={
        "book_id": 1,
        "reader_name": "Иван Иванов",
        "borrow_date": "2023-01-01T00:00:00"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == 1
    assert data["reader_name"] == "Иван Иванов"
    assert data["borrow_date"] == "2023-01-01T00:00:00"


def test_create_borrow_unavailable_book():
    response = client.post("/borrows/", json={
        "book_id": 999,  # несуществующая книга
        "reader_name": "Петр Петров",
        "borrow_date": "2023-01-01T00:00:00"
    })
    assert response.status_code == 400
    data = response.json()
    assert "Книгу с ID 999 недоступна для выдачи." in data['detail']


def test_complete_borrow():
    response = client.patch("/borrows/1/return",
                            json={"return_date": "2023-02-01T00:00:00"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Возврат успешно завершен."


def test_complete_borrow_not_found():
    response = client.patch("/borrows/999/return",
                            json={"return_date": "2023-03-01T00:00:00"})
    assert response.status_code == 404
    data = response.json()
    assert "Запись о выдаче не найдена." in data['detail']
