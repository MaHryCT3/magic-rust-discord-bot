from pydantic import Field, field_validator

from core.api_clients.vk.models.attachements import (
    AttachmentsModels,
    AttachmentTypes,
    DocAttachment,
    LinkAttachment,
    PhotoAttachment,
    PollAttachment,
    VideoAttachment,
)
from core.api_clients.vk.models.base import BaseUpdateEvent

attachment_type_to_object_mapper: dict[AttachmentTypes, type[AttachmentsModels]] = {
    AttachmentTypes.POLL: PollAttachment,
    AttachmentTypes.LINK: LinkAttachment,
    AttachmentTypes.DOC: DocAttachment,
    AttachmentTypes.VIDEO: VideoAttachment,
    AttachmentTypes.PHOTO: PhotoAttachment,
}


class WallPost(BaseUpdateEvent):
    id: int
    text: str
    attachments: list[AttachmentsModels] = Field(default_factory=list)

    @field_validator('attachments', mode='before')
    @classmethod
    def validate_attachments(cls, v: list[dict]) -> list[AttachmentsModels]:
        new_objects: list[AttachmentsModels] = []
        for obj in v:
            if obj['type'] not in list(attachment_type_to_object_mapper.keys()):
                continue  # Не поддерживаемый данный тип

            type = AttachmentTypes(obj['type'])
            model = attachment_type_to_object_mapper[type]

            object_data = obj[type.value]
            new_object = model(**object_data)
            new_objects.append(new_object)

        return new_objects
