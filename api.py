import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def get_users(skip: int = 0, limit: int = 100):
    response = requests.get(f"{BASE_URL}/users")
    response.raise_for_status()
    return response.json()

def update_user_role(user_id: str, role: str):
    response = requests.patch(f"{BASE_URL}/users/{user_id}/role", json={"Role": role})
    response.raise_for_status()
    return response.json()

def get_groups(skip: int = 0, limit: int = 100):
    response = requests.get(f"{BASE_URL}/groups")
    response.raise_for_status()
    return response.json()

def get_cases(skip: int = 0, limit: int = 100):
    response = requests.get(f"{BASE_URL}/cases")
    response.raise_for_status()
    return response.json()

# @dataclass
# class User:
#     UserID: str
#     UserName: str
#     UserPic: str
#     NickName: str

# class UserAPI:
#     def __init__(self, base_url: str = BASE_URL):
#         self.base_url = base_url
#         self.endpoint = f"{base_url}/users"

#     def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
#         """Get list of users"""
#         response = requests.get(
#             self.endpoint,
#             params={"skip": skip, "limit": limit}
#         )
#         response.raise_for_status()
#         return [User(**user) for user in response.json()]

#     def get_user(self, user_id: str) -> User:
#         """Get specific user"""
#         response = requests.get(f"{self.endpoint}/{user_id}")
#         response.raise_for_status()
#         return User(**response.json())

#     def create_user(self, user_data: Dict) -> User:
#         """Create new user"""
#         response = requests.post(self.endpoint, json=user_data)
#         response.raise_for_status()
#         return User(**response.json())

#     def update_user_role(self, user_id: str, role: str) -> User:
#         """Update user role"""
#         response = requests.patch(
#             f"{self.endpoint}/{user_id}/role",
#             json={"Role": role}
#         )
#         response.raise_for_status()
#         return User(**response.json())
