from starlette import status
from ..models import Todos
from .utils import *
from ..routers.todos import get_db,get_current_user


# Creating a fake database
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread":False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine)

# Override get_db to call test db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override get_current_user to mock the logged in user
def override_get_current_user():
    return {"username": "codingwithrobytest","id":1, "user_role":"admin"}

# Override app dependency for testing
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Forcing it to run as Testing application
client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1,
        id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()

def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"complete":False,"title":"Learn to code",
                                "description":"Need to learn everyday","id":1,
                                "priority":5,"owner_id":1}]


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"complete":False,"title":"Learn to code",
                                "description":"Need to learn everyday","id":1,
                                "priority":5,"owner_id":1}


def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail":"Todo not found"}


def test_create_todo(test_todo):
    request_data = {
        "title": "New todo!",
        "description": "New todo description",
        "priority": 5,
        "complete": False
    }
    response = client.post("/todos/todo/",json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")


def test_update_todo(test_todo):
    request_data = {
        "title": "Change title of the todo already saved",
        "description": "Need to learn everyday!",
        "priority": 5,
        "complete": False
    }
    response = client.put("/todos/todo/1",json=request_data)
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == "Change title of the todo already saved"


def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "Change title of the todo already saved",
        "description": "Need to learn everyday!",
        "priority": 5,
        "complete": False
    }
    response = client.put("/todos/todo/999",json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete("/todos/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}