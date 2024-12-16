from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from app.models import Author, Book, Borrow

app = FastAPI()


# Создаем сессию базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Автор
class AuthorIn(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[str]


# Книга
class BookIn(BaseModel):
    title: str
    description: Optional[str]
    author_id: int
    available_copies: int


# Выдача
class BorrowIn(BaseModel):
    book_id: int
    reader_name: str
    borrow_date: str
    return_date: Optional[str]


# Проверка доступности книги перед выдачей
def check_availability(book_id: int, db: Session):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book or book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Книга с ID {book_id} недоступна для выдачи."
        )
    else:
        book.available_copies -= 1
        db.commit()


# Увеличение количества доступных экземпляров после возврата
def increase_available_copies(book_id: int, db: Session):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        book.available_copies += 1
        db.commit()


# Создание записи о выдаче книги
@app.post("/borrows/")
async def create_borrow(borrow: BorrowIn, db:
                        Session = Depends(get_db)):
    check_availability(borrow.book_id, db)
    new_borrow = Borrow(book_id=borrow.book_id,
                        reader_name=borrow.reader_name,
                        borrow_date=borrow.borrow_date,
                        return_date=borrow.return_date)
    db.add(new_borrow)
    db.commit()
    db.refresh(new_borrow)
    return new_borrow


# Завершение выдачи книги
@app.patch("/borrows/{id}/return")
async def complete_borrow(id: int, return_date: str, db:
                          Session = Depends(get_db)):
    borrow = db.query(Borrow).filter(Borrow.id == id).first()
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись о выдаче не найдена.")
    book_id = borrow.book_id
    borrow.return_date = return_date
    db.commit()
    increase_available_copies(book_id, db)
    return {"message": "Возврат успешно завершен."}
