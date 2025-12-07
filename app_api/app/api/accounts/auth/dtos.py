"""Authentication data transfer objects (DTOs).

This module defines the data structures used for authentication requests
and their corresponding Litestar DTOs for validation and serialization.
"""

from dataclasses import dataclass

from litestar.dto import DataclassDTO


@dataclass
class Login:
    """Login credentials."""

    username: str
    password: str


class LoginDTO(DataclassDTO[Login]):
    """DTO for login."""
