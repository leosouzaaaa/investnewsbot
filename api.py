from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth import verify_user
import jwt, datetime
from app.config import STOCKS, CRYPTOS
from app.analyzer import generate_suggestions
app = FastAPI(); oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
SECRET_KEY = 'change_this_secret_in_env'
def create_token(username: str):
    payload = {'sub': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
@app.post('/login')
def login(username: str, password: str):
    user = verify_user(username, password)
    if not user: raise HTTPException(status_code=401, detail='Usuário ou senha incorretos')
    token = create_token(username); return {'access_token': token, 'token_type':'bearer'}
@app.get('/recommendations/daily')
def daily(token: str = Depends(oauth2_scheme)):
    return generate_suggestions(STOCKS, CRYPTOS)['daily']
