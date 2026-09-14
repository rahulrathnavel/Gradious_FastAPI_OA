from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas, database
from middleware import RequestTimeMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="LibraFlow - Digital Library System")
app.add_middleware(RequestTimeMiddleware)

def check_staff(x_role: str | None = Header(None)):
    if x_role != "staff":
        raise HTTPException(status_code=403, detail="Only staff users can add books")
    return x_role

@app.get("/books", response_model=list[schemas.BookResponse])
def get_books(
    title: str | None = None,
    author: str | None = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Book)
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    if author:
        query = query.join(models.Author).filter(models.Author.name.ilike(f"%{author}%"))
    return query.all()

@app.get("/books/{isbn}", response_model=schemas.BookResponse)
def get_book(isbn: str, db: Session = Depends(database.get_db)):
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Not Found")
    return book

@app.post("/books", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(database.get_db),
    role: str = Depends(check_staff)
):
    db_book = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Duplicate ISBN")
    
    # Handle nested author
    db_author = db.query(models.Author).filter(models.Author.name == book.author.name).first()
    if not db_author:
        db_author = models.Author(name=book.author.name, biography=book.author.biography, birth_year=book.author.birth_year)
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
    
    new_book = models.Book(
        isbn=book.isbn,
        title=book.title,
        published_year=book.published_year,
        is_available=book.is_available,
        author_id=db_author.id
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.patch("/books/{isbn}/borrow", response_model=schemas.BookResponse)
def borrow_book(isbn: str, db: Session = Depends(database.get_db)):
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Not Found")
    
    if not book.is_available:
        raise HTTPException(status_code=400, detail="Book already borrowed")
        
    book.is_available = False
    db.commit()
    db.refresh(book)
    return book

@app.get("/authors", response_model=list[schemas.AuthorBookCount])
def get_authors(db: Session = Depends(database.get_db)):
    results = db.query(models.Author.name, func.count(models.Book.isbn).label('book_count')).join(models.Book).group_by(models.Author.id).all()
    return [{"name": r[0], "book_count": r[1]} for r in results]

