# # from typing import Optional
# # import uuid
# # from datetime import datetime
# # from pydantic import BaseModel, EmailStr


# # class UserBase(BaseModel):
# #     name: str
# #     email: EmailStr
# #     career_goal: str | None = None

# # # class UserCreate(UserBase):
# # #     password: str
# # #     email: EmailStr
# # #     password: str
# # #     career_goal: Optional[str]
# # class UserCreate(UserBase):
# #     password: str
# #     career_goal: Optional[str] = None


# # class UserOut(UserBase):
# #     id: uuid.UUID
# #     created_at: datetime
# #     name: str
# #     email: EmailStr
# #     career_goal: Optional[str]

# #     class Config:
# #         from_attributes = True
# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from uuid import UUID
# from datetime import datetime


# class UserCreate(BaseModel):
#     name: str
#     email: EmailStr
#     password: str
#     career_goal: Optional[str] = None


# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str


# class UserResponse(BaseModel):
#     id: UUID
#     name: str
#     email: EmailStr
#     career_goal: Optional[str] = None
#     created_at: datetime

#     class Config:
#         from_attributes = True


# class AuthResponse(BaseModel):
#     access_token: str
#     token_type: str
#     user: UserResponse


from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    career_goal: Optional[str] = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    career_goal: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Aliases for backward compatibility
UserResponse = UserOut


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# Keep old Token schema if anything else imports it
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str