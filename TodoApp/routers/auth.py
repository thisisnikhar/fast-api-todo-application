from datetime import timedelta,datetime,timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from starlette import status

from ..database import SessionLocal

# Step 4: Importing passlib for encrypting password
from passlib.context import CryptContext

# Step 2: Importing Users model
from ..models import Users
from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt,JWTError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "v4w6JWRcPIUfHcYZM95q9HxXVSVUnpy0vN1dQDmoECq"
ALGORITHM = "HS256"

# Step 5: Instantiate BCrypt Context
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Step 6: Add db_dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Step 7: Create db_dependency
db_dependency = Annotated[Session,Depends(get_db)] # Import Session from sqlalchemy.orm and Depends from fastapi

templates = Jinja2Templates(directory="TodoApp/templates")


### Pages ###

@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse(request=request,name="login.html")


@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse(request=request,name="register.html")

### Endpoints ###

def authenticate_user(username:str,password:str,db):
    # Fetch user from db
    user = db.query(Users).filter(Users.username == username).first()
    print(user)
    if not user:
        return False
    # Verify the password
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int,role: str, expires_delta: timedelta):
    encode = {"sub":username,"id":user_id,"role":role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp":expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)


async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        userid: int = payload.get("id")
        userrole: str = payload.get("role")
        phone_number: str = payload.get("phone_number")
        password: str = payload.get("password")
        if username is None or userid is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
        return {"username": username, "id": userid, "userrole": userrole,"phone_number": phone_number, "password": password}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")


# Step 1: Creating Pydantic class for new user
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,create_user_request: CreateUserRequest):
    # Step 3: Creating users
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        phone_number = create_user_request.phone_number,
        hashed_password = bcrypt_context.hash(create_user_request.password), # Hashing the password
        is_active = True
    )
    # Adding user to database
    db.add(create_user_model)
    db.commit()


@router.post("/token",response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username,form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")
    token = create_access_token(user.username,user.id,user.role, timedelta(minutes=20))
    return {"access_token": token,"token_type": "bearer"}
