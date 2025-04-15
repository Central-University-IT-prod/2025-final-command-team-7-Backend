import typing


class Committer(typing.Protocol):
    async def commit(self) -> None:
        raise NotImplementedError
