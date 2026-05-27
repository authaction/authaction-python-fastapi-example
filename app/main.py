from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI

from app.auth.jwt_bearer import JWTBearer

app = FastAPI(title="AuthAction FastAPI Example")

jwt_bearer = JWTBearer()


@app.get("/public")
def public_route():
    return {"message": "This is a public message!"}


@app.get("/protected")
def protected_route(payload: dict = Depends(jwt_bearer)):
    return {"message": "This is a protected message!", "sub": payload.get("sub")}
