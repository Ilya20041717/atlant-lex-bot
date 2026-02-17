from aiogram.filters import BaseFilter


class RoleFilter(BaseFilter):
    def __init__(self, *roles: str) -> None:
        self.roles = set(roles)

    async def __call__(self, event, **kwargs) -> bool:
        role = kwargs.get("role")
        return role in self.roles
