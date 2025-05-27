import os
import pytest
from unittest.mock import patch
from lunarbase.domains.user.user_context import UserContext
from lunarbase.domains.user.models import UserModel

@pytest.fixture
def user_context():
    return UserContext()

def test_user_context_initialization(user_context):
    assert user_context._user is None

@patch.dict(os.environ, {"LUNAR_USERID": "test-user-123"})
def test_user_context_with_user_id(user_context):
    user = user_context.user
    assert user is not None
    assert isinstance(user, UserModel)
    assert user.id == "test-user-123"
    

    assert user_context.user is user

@patch.dict(os.environ, {}, clear=True)
def test_user_context_without_user_id(user_context):
    user = user_context.user
    assert user is None

@patch.dict(os.environ, {"LUNAR_USERID": "test-user-123"})
def test_user_context_caching(user_context):
    user1 = user_context.user
    assert user1 is not None
    
    del os.environ["LUNAR_USERID"]
    
    user2 = user_context.user
    assert user2 is user1 