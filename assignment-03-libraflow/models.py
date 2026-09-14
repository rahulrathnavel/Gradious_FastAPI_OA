from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    biography = Column(String, nullable=True)
    birth_year = Column(Integer, nullable=True)

    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(13), primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    published_year = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)

    author = relationship("Author", back_populates="books")

