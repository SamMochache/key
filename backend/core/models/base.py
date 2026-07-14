from .uuid import UUIDModel
from .timestamp import TimeStampedModel
from .soft_delete import SoftDeleteModel


class BaseModel(
    UUIDModel,
    TimeStampedModel,
    SoftDeleteModel,
):
    """
    Base model inherited by most business models.
    """

    class Meta:
        abstract = True