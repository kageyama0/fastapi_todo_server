from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request
from pydantic import BaseModel
# dockerの時はこっち
# from .db import Todo, engine
# 普通にMacでやるときはこっち
from db import Todo, engine
from fastapi.templating import Jinja2Templates

# DB接続用のセッションクラス インスタンスが作成されると接続する
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テンプレートファイル
templates = Jinja2Templates(directory="templates")
jinja_env = templates.env

# Pydanticを用いたAPIに渡されるデータの定義 ValidationやDocumentationの機能が追加される
class TodoIn(BaseModel):
    title: str
    done: bool

# 単一のTodoを取得するためのユーティリティ
def get_todo(db_session: Session, todo_id: int):
    return db_session.query(Todo).filter(Todo.id == todo_id).first()

# DB接続のセッションを各エンドポイントの関数に渡す
def get_db(request: Request):
    return request.state.db


# このインスタンスをアノテーションに利用することでエンドポイントを定義できる
app = FastAPI()

# Todoの全取得
@app.get("/todos/")
async def read_todos(request:Request, db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return templates.TemplateResponse("todo.html", {"request": request, "todos": todos})


# 単一のTodoを取得
@app.get("/todos/{todo_id}")
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)
    return todo

# Todoを登録
@app.post("/todos/")
async def create_todo(todo_in: TodoIn, db: Session = Depends(get_db)):
    todo = Todo(title=todo_in.title, done=todo_in.done)
    db.add(todo)
    db.commit()
    todo = get_todo(db, todo.id)
    return todo

# Todoを更新
@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo_in: TodoIn, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)
    todo.title = todo_in.title
    todo.done = todo_in.done
    db.commit()
    todo = get_todo(db, todo_id)
    return todo

# Todoを削除
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)
    db.delete(todo)
    db.commit()

# リクエストの度に呼ばれるミドルウェア DB接続用のセッションインスタンスを作成
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response
