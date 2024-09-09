from enum import StrEnum
from typing import TypeAlias

from pydantic import BaseModel, Field, field_validator


class AttachmentTypes(StrEnum):
    PHOTO = 'photo'
    VIDEO = 'video'
    AUDIO = 'audio'
    DOC = 'doc'
    LINK = 'link'
    POLL = 'poll'


class MediaSizes(BaseModel):
    url: str
    width: int
    height: int


class BaseAttachment:
    attachment_type: AttachmentTypes


class PhotoAttachment(BaseModel, BaseAttachment):
    class OrigPhoto(BaseModel):
        url: str

    attachment_type: AttachmentTypes = AttachmentTypes.PHOTO
    orig_photo: OrigPhoto


class VideoAttachment(BaseModel, BaseAttachment):
    attachment_type: AttachmentTypes = AttachmentTypes.VIDEO
    image: list[MediaSizes] = Field(default_factory=list)


class LinkAttachment(BaseModel, BaseAttachment):
    attachment_type: AttachmentTypes = AttachmentTypes.LINK
    url: str


class PollAttachment(BaseModel, BaseAttachment):
    attachment_type: AttachmentTypes = AttachmentTypes.POLL
    created: int  # timestamp
    end_date: int  # timestamp
    multiple: bool
    question: str
    answers: list[str]

    @field_validator('answers', mode='before')
    @classmethod
    def answers_validator(cls, v: list[dict], _) -> list[str]:
        return [v['text'] for v in v]


class DocAttachment(BaseModel, BaseAttachment):
    attachment_type: AttachmentTypes = AttachmentTypes.DOC
    url: str
    title: str


AttachmentsModels: TypeAlias = PollAttachment | LinkAttachment | DocAttachment | VideoAttachment | PhotoAttachment
