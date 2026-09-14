# ChefPalette — Recipe Sharing API

## Objective
Build a FastAPI-based Recipe Sharing API with list-based validation, complex filters, partial search, likes, and trending logic.

## Features
- Dependency Injection for Database Sessions
- List-based Pydantic Models for ingredients
- Partial Matching for ingredient search
- Like Count Aggregation (Trending sorted descending)
- Prevent Duplicate Likes

## Setup & Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Testing
```bash
python -m pytest
```

