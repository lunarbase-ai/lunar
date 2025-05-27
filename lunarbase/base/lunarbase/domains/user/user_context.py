import os
from typing import Optional
from .models import UserModel
from lunarbase.utils import setup_logger

USER_CONTEXT_LOGGER = setup_logger("lunarbase-user-context")

class UserContext:
    user: Optional[UserModel]
    def __init__(self):
        pass

    def get_user(self) -> Optional[UserModel]:
        user_id = os.environ.get("LUNAR_USERID")
        if user_id is None:
            USER_CONTEXT_LOGGER.warning("No user ID found in environment")
            return None
        return UserModel(id=user_id)