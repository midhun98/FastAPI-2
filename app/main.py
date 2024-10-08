from typing import List

import psycopg2
from fastapi import FastAPI, HTTPException, Depends
from fastapi import status
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session

from . import models
from . import utils
from .database import engine, get_db
from .schemas import PostCreate, Post, UserCreate, UserOut

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

try:
    conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="root", port=5432,
                            cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection established")
except psycopg2.Error as e:
    print(e)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/posts", response_model=List[Post])
async def posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=201, response_model=Post)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}", response_model=Post)
async def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE ID = %s""", (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/posts/{id}", status_code=204)
async def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE ID = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() is None:
        raise HTTPException(status_code=404, detail="Post not found")

    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "Post deleted"}


@app.put("/posts/{id}", status_code=200)
async def update_post(id: int, updated_post: PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title= %s, content = %s, published=%s  WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
