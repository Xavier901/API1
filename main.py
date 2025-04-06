from fastapi import FastAPI,HTTPException,status,Response
from fastapi.params import Body

from typing import Optional
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app=FastAPI()






while True:
    try:
        conn=psycopg2.connect(host='localhost',database='fastapi',user='postgres',
                          password='root',cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("database connection is sucessfull")
        break
    except Exception as error:
        print("Failled",error)
        time.sleep(2)
      
class Post(BaseModel):
    title:str
    content:str
    published:bool=True

my_post=[{"title":"title of post 1","content":"Content of post 1","id":1},
         {"title":"title of post 2","content":"Content of post 2","id":2}]

@app.get("/")
def index():
    return{"message":"Hello world"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM post""")
    posts=cursor.fetchall()
    print(posts)
    return{"post":posts}

@app.post("/post")
def create_post(post: Post):
    cursor.execute(""" INSERT INTO post (title,content,published) VALUES (%s,%s,%s) RETURNING * """,
                   (post.title,post.content,post.published))
    new_post=cursor.fetchone()
    conn.commit()
    return{"data":new_post}

@app.get("/posts/{id}")
def get_post(id:int):
    cursor.execute("""SELECT * FROM post WHERE id = %s """,(str(id),))
    post=cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} was not found")
    return {"post_detail":post}

@app.delete("/post/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):    
    cursor.execute("""DELETE FROM post WHERE id= %s returning *""",(str(id),))
    deleted_post=cursor.fetchone()
    print(deleted_post)
    conn.commit()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} does not exist.")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/post/{id}")
def update_post(id:int,post:Post):
    cursor.execute("""UPDATE post SET title = %s,content=%s,published=%s WHERE id=%s returning *""",(post.title,post.content,
                                                                             post.published,str(id),))
    updated_post=cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} doesn't exist")
    return{"updated":updated_post}
    
    