from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Path, APIRouter
from ..models import Todos
from ..database import SessionLocal
from pydantic import BaseModel,Field

from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0,lt=6)
    complete: bool


@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id==user.get('id')).all()


@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency,db:db_dependency,todo_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    # Querying the database
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(
        Todos.owner_id == user.get('id')).first()
    # Above query returns the first match

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="Todo not found")


@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency,db:db_dependency,todo_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    todo_model = Todos(**todo_request.model_dump(),owner_id=user.get("id")) # Converting request to Python object, adding owner_id

    db.add(todo_model) # Adding the object to the session
    db.commit() # Saving to database


@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency,db:db_dependency,todo_request:TodoRequest,todo_id:int=Path(gt=0)):
    if user is None:
        return HTTPException(status_code=401,detail="Authentication failed")
    # Step 1: Fetch the existing record
    todo_model = db.query(Todos).filter(Todos.owner_id == user.get("id")).filter(
        Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")

    # Step 2: Update the record
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.complete = todo_request.complete
    todo_model.priority = todo_request.priority

    # Step 3: Commit the changes
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id==todo_id).filter(
        Todos.owner_id==user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")
    db.query(Todos).filter(Todos.id==todo_id).filter(
        Todos.owner_id==user.get("id")).delete()
    db.commit()