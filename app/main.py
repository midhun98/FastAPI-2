import psycopg2
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor

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

@app.get("/posts")
async def posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return posts