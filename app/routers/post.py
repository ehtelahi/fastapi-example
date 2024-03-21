from fastapi import status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from .. import oauth2

router = APIRouter(prefix="/posts", tags=["Posts"])

my_posts = [{
    "id": 1,
    "title": "Post 1",
    "description": "This is the first post",
    "published": True,
    "rating": 5
},
{
    "id": 2,
    "title": "Post 2",
    "description": "This is the second post",
    "published": False,
    "rating": 3
}]

def find_post(id: int):
    for post in my_posts:
        if post['id'] == id:
            return post

def find_index_post(id: int):
    for index, post in enumerate(my_posts):
        if(post['id'] == id):
            return index

@router.get("", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: str = ""):
    posts = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.ilike(f"%{search}%")).limit(limit).offset(skip).all()
    print(posts)
    return posts

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # print(current_user.email)
    post = post.model_dump()
    # new_post = models.Post(title = post['title'], content = post['content'], published = post['published'])
    new_post = models.Post(owner_id=current_user.id, **post)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    # post['id'] = len(my_posts) + 1
    # my_posts.append(post)
    return new_post

@router.get("/latest")
def get_latest_post():
    return {"data": my_posts[-1]}

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # post = find_post(id)
    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
    #     response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # index = find_index_post(id)
    post_query = db.query(models.Post).filter(models.Post.id == id);

    post = post_query.first()

    # if index == None:
    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    post_query.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # index = find_index_post(id)
    post_query = db.query(models.Post).filter(models.Post.id == id);

    post = post_query.first()

    # if index == None:
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    # my_posts[index] = post

    return post_query.first()
    # return {"data": my_posts[index]}