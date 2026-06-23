from typing import Literal

from pydantic import BaseModel, Field


Category = Literal["notes", "tech", "works"]
PostStatus = Literal["draft", "published"]
ModerationStatus = Literal["pending", "approved", "hidden"]


class PostPayload(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    slug: str = Field(min_length=1, max_length=160, pattern=r"^[a-z0-9][a-z0-9-]*$")
    excerpt: str = Field(default="", max_length=500)
    body: str = Field(min_length=1)
    category: Category
    status: PostStatus = "draft"
    published_at: str | None = None


class InteractionPayload(BaseModel):
    nickname: str = Field(min_length=1, max_length=40)
    content: str = Field(min_length=1, max_length=1000)


class LoginPayload(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)


class ModerationPayload(BaseModel):
    status: ModerationStatus


class VisitPayload(BaseModel):
    path: str = Field(default="/", min_length=1, max_length=300)
    slug: str | None = Field(default=None, max_length=160)
