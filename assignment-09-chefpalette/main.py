from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChefPalette - Recipe Sharing API")

auth_router = APIRouter(prefix="/auth", tags=["auth"])
recipes_router = APIRouter(prefix="/recipes", tags=["recipes"])

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


def _serialize_recipe(recipe: models.Recipe) -> dict:
    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": [i.name for i in recipe.ingredients],
        "instructions": recipe.instructions,
        "prep_time": recipe.prep_time,
        "user_id": recipe.user_id
    }

@recipes_router.post("", response_model=schemas.RecipeResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe: schemas.RecipeCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not recipe.ingredients:
        raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")

    db_recipe = models.Recipe(
        title=recipe.title,
        instructions=recipe.instructions,
        prep_time=recipe.prep_time,
        user_id=current_user.id
    )
    db.add(db_recipe)
    db.flush()
    
    for ing in recipe.ingredients:
        db_ing = models.RecipeIngredient(recipe_id=db_recipe.id, name=ing)
        db.add(db_ing)
        
    db.commit()
    db.refresh(db_recipe)
    return _serialize_recipe(db_recipe)

@recipes_router.get("/trending", response_model=list[schemas.TrendingRecipeResponse])
def get_trending_recipes(db: Session = Depends(get_db)):
    # Sort by like count descending
    recipes = db.query(models.Recipe, func.count(models.Like.id).label("like_count"))\
                .outerjoin(models.Like)\
                .group_by(models.Recipe.id)\
                .order_by(func.count(models.Like.id).desc())\
                .all()
    
    results = []
    for r, count in recipes:
        data = _serialize_recipe(r)
        data["like_count"] = count
        results.append(data)
        
    return results

@recipes_router.get("", response_model=list[schemas.RecipeResponse])
def get_recipes(
    ingredient: str | None = None,
    min_prep_time: int | None = None,
    max_prep_time: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Recipe)
    
    if ingredient:
        query = query.join(models.RecipeIngredient).filter(models.RecipeIngredient.name.ilike(f"%{ingredient}%"))
        
    if min_prep_time is not None:
        query = query.filter(models.Recipe.prep_time >= min_prep_time)
        
    if max_prep_time is not None:
        query = query.filter(models.Recipe.prep_time <= max_prep_time)
        
    recipes = query.all()
    return [_serialize_recipe(r) for r in recipes]


@recipes_router.post("/{id}/like", status_code=status.HTTP_201_CREATED)
def like_recipe(
    id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    existing_like = db.query(models.Like).filter(
        models.Like.user_id == current_user.id,
        models.Like.recipe_id == id
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="Duplicate like")
        
    new_like = models.Like(user_id=current_user.id, recipe_id=id)
    db.add(new_like)
    db.commit()
    return {"message": "Recipe liked successfully"}

@recipes_router.put("/{id}", response_model=schemas.RecipeResponse)
def update_recipe(
    id: int,
    update_data: schemas.RecipeUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
        
    if recipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recipe")
        
    if update_data.instructions is not None:
        recipe.instructions = update_data.instructions
        
    if update_data.ingredients is not None:
        if not update_data.ingredients:
            raise HTTPException(status_code=422, detail="Ingredients list cannot be empty")
            
        # Delete old ingredients
        db.query(models.RecipeIngredient).filter(models.RecipeIngredient.recipe_id == id).delete()
        # Add new ingredients
        for ing in update_data.ingredients:
            db.add(models.RecipeIngredient(recipe_id=id, name=ing))
            
    db.commit()
    db.refresh(recipe)
    return _serialize_recipe(recipe)

app.include_router(auth_router)
app.include_router(recipes_router)
