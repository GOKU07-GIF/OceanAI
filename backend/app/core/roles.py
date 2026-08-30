from enum import Enum


class UserRole(str, Enum):
    """
    User roles for OceanAI.
    """

    SUPER_ADMIN = "SUPER_ADMIN"

    ADMIN = "ADMIN"

    MANAGER = "MANAGER"

    SCIENTIST = "SCIENTIST"

    OPERATOR = "OPERATOR"

    VIEWER = "VIEWER"