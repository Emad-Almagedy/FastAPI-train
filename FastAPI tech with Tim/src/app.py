from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from src.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from src.db import create_db_and_tables, get_async_session, Post, User

# for setting the databse creation 
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select 

# using imagekit API image storage
from src.images import imagekit
from pathlib import Path
import shutil, os, uuid, tempfile

# for implementing user login and authentication 
from src.users import auth_backend, current_active_user, fastapi_users



# create the database if not created 
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

# creating a FastAPI application instance
app = FastAPI(lifespan=lifespan)

# registering the routes provided by fastapi_users in the app
# they will be accessed in the docs under the "auth" section
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"])
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)

# upload a post with a photo or a video
#You use session so your endpoint can save the uploaded file’s data into the database, and you use AsyncSession + Depends so it happens safely and efficiently.

# ---------- UPLOAD ENDPOINT ----------
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends (current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Upload a file (image or video) to ImageKit and save record in DB.
    - Small files: directly from bytes
    - Large files: via temporary file
    """
    temp_file_path = None
    try:
        # Use temp file for uploads
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        #upload the data from the temp file 
        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.files.upload(
                file = f.read(),
                file_name = file.filename,
                folder="/posts",
                tags=["developer project"]
            )

        # Get uploaded file URL
        url = upload_result.url
        if not url:
            raise HTTPException(status_code=500, detail="ImageKit upload failed")

        # Save post in database
        post = Post(
            user_id = user.id,
            caption=caption,
            url=url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=upload_result.name
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    finally:
        # Cleanup temp file if used
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

            

# view posts
@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = result.scalars().all()
    
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {user.id: user.email for user in users}
    
    
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id" : str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "unknown")
            }
        )
    return  {"posts" : posts_data} 

# delete a post 
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_active_user)
                ):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="post not found")
        
        # if the loged in user is not the user who made the post
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to delete this post")
        
        await session.delete(post)
        await session.commit()
        
        return {"success": True, "message":"post deleted successfully"}
    
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=str(e))
        