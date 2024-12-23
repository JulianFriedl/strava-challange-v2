from datetime import datetime
from utils.datetime_utils import parse_datetime

class Profile:
    def __init__(self, medium: str, full: str):
        self.medium = medium
        self.full = full


class Tokens:
    def __init__(self, access_token: str, refresh_token: str, expires_at: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at


class Athlete:
    def __init__(
        self,
        athlete_id: int,
        username: str,
        first_name: str,
        last_name: str,
        created_at: datetime,
        profile: Profile,
        tokens: Tokens,
    ):
        self.athlete_id = athlete_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = parse_datetime(created_at)
        self.profile = profile
        self.tokens = tokens

    @classmethod
    def from_mongo(cls, data):
        """
        Convert a MongoDB document to an Athlete instance.
        """
        return cls(
            athlete_id=data["athlete_id"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            created_at=data["created_at"],
            profile=data["profile"],
            tokens=data["tokens"],
        )

    def to_mongo(self):
        """
        Convert an Athlete instance to a MongoDB-compatible dictionary.
        """
        return {
            "athlete_id": self.athlete_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at,
            "profile": self.profile,
            "tokens": self.tokens,
        }

    def to_dict(self):
        return {
            "athlete_id": self.athlete_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "profile": self.profile,
            # Note: Exclude tokens if returning this data to the frontend
        }

