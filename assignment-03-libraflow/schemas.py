from pydantic import BaseModel, Field

class AuthorBase(BaseModel):
    name: str
    biography: str | None = None
    birth_year: int | None = None

class AuthorCreate(AuthorBase):
    pass

class AuthorResponse(AuthorBase):
    id: int
    class Config:
        from_attributes = True

class BookBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=13)
    title: str
    published_year: int
    is_available: bool = True

class BookCreate(BookBase):
    author: AuthorCreate

class BookResponse(BookBase):
    author: AuthorBase

    class Config:
        from_attributes = True

class AuthorBookCount(BaseModel):
    name: str
    book_count: int

