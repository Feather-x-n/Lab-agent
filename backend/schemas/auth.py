from pydantic import BaseModel
from schemas.user import UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
  token: str
  user: UserResponse
class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str | None = None
class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str