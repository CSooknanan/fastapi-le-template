import uvicorn
from fastapi import FastAPI, Request, status, Form
from fastapi.responses import RedirectResponse
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import get_settings
from app.dependencies import IsUserLoggedIn, SessionDep, AuthDep
from fastapi.templating import Jinja2Templates
from app.utilities import get_flashed_messages
from jinja2 import Environment, FileSystemLoader
from sqlmodel import select
from app.models import User
from app.utilities import flash, create_access_token
from fastapi.staticfiles import StaticFiles
from app.models import Album, Track, Comment
from fastapi import Form
from typing import Optional


app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
]
)
template_env = Environment(loader = FileSystemLoader("app/templates",), )
template_env.globals['get_flashed_messages'] = get_flashed_messages
templates = Jinja2Templates(env=template_env)
static_files = StaticFiles(directory="app/static")

app.mount("/static", static_files, name="static")


@app.get('/', response_class=RedirectResponse)
async def index_view(
  request: Request,
  user_logged_in: IsUserLoggedIn,
):
  if user_logged_in:
    return RedirectResponse(url=request.url_for('home_view'), status_code=status.HTTP_303_SEE_OTHER)
  return RedirectResponse(url=request.url_for('login_view'), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login")
async def login_view(
  user_logged_in: IsUserLoggedIn,
  request: Request,
):
  if user_logged_in:
    return RedirectResponse(url=request.url_for('home_view'), status_code=status.HTTP_303_SEE_OTHER)
  return templates.TemplateResponse(
          request=request, 
          name="login.html",
      )

@app.post('/login')
def login_action(
  request: Request,
  db: SessionDep,
  username: str = Form(),
  password: str = Form(),
):
  
  user = db.exec(select(User).where(User.username == username)).one_or_none()
  if user and user.check_password(password):
    response = RedirectResponse(url=request.url_for("index_view"), status_code=status.HTTP_303_SEE_OTHER)
    access_token = create_access_token(data={"sub": f"{user.id}"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        samesite="lax",
        secure=True,
    )    
    return response
  else:
    flash(request, 'Invalid username or password')
    return RedirectResponse(url=request.url_for('login_view'), status_code=status.HTTP_303_SEE_OTHER)


@app.get('/app')
def home_view(
  request: Request,
  user: AuthDep,
  db: SessionDep,
  album_id: Optional[int] = None,
  track_id: Optional[int] = None,
):
  albums =db.exec(select(Album)).all()
  selected_album = None
  selected_track = None

  if album_id:
    selected_album = db.exec(select(Album).where(Album.id == album_id)).first()

  if track_id:
    selected_track = db.exec(select(Track).where(Track.id == track_id)).first()
    if selected_track and not selected_album:
      selected_album = selected_track.album

  return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
      "request": request,
      "current_user": user,
      "albums": albums,
      "selected_album": selected_album,
      "selected_track": selected_track,
    }
  )

@app.post('/comment/{track_id}')
def add_comment_action(request: Request, track_id: int, user: AuthDep, db: SessionDep, text: str = Form(...)):
    # Notice we are now saving user_id=user.id!
    new_comment = Comment(text=text, track_id=track_id, user_id=user.id)
    db.add(new_comment)
    db.commit()
    
    track = db.exec(select(Track).where(Track.id == track_id)).first()
    return RedirectResponse(url=f"/app?album_id={track.album_id}&track_id={track.id}", status_code=status.HTTP_303_SEE_OTHER)



@app.get('/delete_comment/{comment_id}')
def delete_comment_action(request: Request, comment_id: int, user: AuthDep, db: SessionDep):
    comment = db.exec(select(Comment).where(Comment.id == comment_id)).first()
    
    # Security: Only delete if the comment exists AND belongs to the logged-in user
    if comment and comment.user_id == user.id:
        track_id = comment.track_id
        album_id = comment.track.album_id
        db.delete(comment)
        db.commit()
        return RedirectResponse(url=f"/app?album_id={album_id}&track_id={track_id}", status_code=status.HTTP_303_SEE_OTHER)
        
    return RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)

@app.get('/like/{track_id}')
def like_action(request: Request, track_id: int, user: AuthDep, db: SessionDep):
    track = db.exec(select(Track).where(Track.id == track_id)).first()
    if track:
        track.likes += 1
        db.add(track)
        db.commit()
        return RedirectResponse(url=f"/app?album_id={track.album_id}&track_id={track.id}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)


@app.get('/dislike/{track_id}')
def dislike_action(request: Request, track_id: int, user: AuthDep, db: SessionDep):
    track = db.exec(select(Track).where(Track.id == track_id)).first()
    if track:
        track.dislikes += 1
        db.add(track)
        db.commit()
        return RedirectResponse(url=f"/app?album_id={track.album_id}&track_id={track.id}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/app", status_code=status.HTTP_303_SEE_OTHER)

@app.get('/logout')
async def logout(request: Request):
  response = RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
  response.delete_cookie(
      key="access_token", 
      httponly=True,
      samesite="none",
      secure=True
  )
  flash(request, 'logged out')
  return response