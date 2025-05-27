import os
from typing import Optional
from .models import UserModel
from lunarbase.utils import setup_logger

USER_CONTEXT_LOGGER = setup_logger("lunarbase-user-context")

class UserContext:
    _user: Optional[UserModel]

    def __init__(self):
        self._user = None

    @property
    def user(self) -> Optional[UserModel]:
        if self._user is not None:
            return self._user
        
        user_id = os.environ.get("LUNAR_USERID")
        if user_id is None:
            USER_CONTEXT_LOGGER.warning("No user ID found in environment")
            return None
        
        self._user = UserModel(id=user_id)
        return self._user