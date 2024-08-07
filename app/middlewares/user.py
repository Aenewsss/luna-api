import json
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from requests import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.database.database import get_db
from app.models.models import User

class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print('line 12', request.url.path, request.method)
        if request.url.path == "/wpp-webhook" and request.method == "POST":
            try:
                body = await request.body()
                body = json.loads(body)
                
                user_phone = body.get("user_phone")

                if user_phone:
                    db: Session = next(get_db())

                    user = db.query(User).filter(User.phone == user_phone).first()

                    if not user:
                        raise HTTPException(status_code=404, detail="User not found")

                    request.state.user_id = user.id
                    request.state.user_name = user.name
                
                response = await call_next(request)

                return response
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail},
                )
            except json.JSONDecodeError as e:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid JSON in request body"},
                )
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"detail": str(e)},
                )

        response = await call_next(request)
        return response
