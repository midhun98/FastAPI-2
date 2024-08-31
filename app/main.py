import psycopg2
from fastapi import FastAPI, HTTPException, Depends
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

try:
    conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="root", port=5432,
                            cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection established")
except psycopg2.Error as e:
    print(e)


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/posts")
async def posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return posts


@app.post("/posts", status_code=201)
async def create_post(post: PostBase):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"message": new_post}


@app.get("/posts/{id}")
async def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE ID = %s""", (str(id),))
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/posts/{id}", status_code=204)
async def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE ID = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=404, detail="Post not found")


@app.put("/posts/{id}", status_code=200)
async def update_post(id: int, post: PostBase):
    cursor.execute("""UPDATE posts SET title= %s, content = %s, published=%s  WHERE id = %s RETURNING *""",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": updated_post}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status": "success"}
