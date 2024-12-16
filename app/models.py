from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_date = Column(DateTime)

    books = relationship('Book', back_populates='author')


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))
    author_id = Column(Integer, ForeignKey('authors.id'))
    available_copies = Column(Integer, default=0)

    author = relationship('Author', back_populates='books')
    borrows = relationship('Borrow', back_populates='book')


class Borrow(Base):
    __tablename__ = 'borrows'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    reader_name = Column(String(100), nullable=False)
    borrow_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)

    book = relationship('Book', back_populates='borrows')
