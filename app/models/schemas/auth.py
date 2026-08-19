from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: str
    user_name: str


class LoginResponse(BaseModel):
    token: str
    user: UserProfile
