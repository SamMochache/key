from .timestamp import TimeStampedModel
from .uuid import UUIDModel


class IdentityBaseModel(
    UUIDModel,
    TimeStampedModel,
):
    """
    Base model for authentication-related models.

    Identity models should never inherit soft delete.
    """

    class Meta:
        abstract = True