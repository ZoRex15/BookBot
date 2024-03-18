from app.database.models import User, Bookmark

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, and_, select

from typing import List

class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, id: int) -> None:
        user = await self.session.get(User, id)
        if not user:
            user = User(
                id=id
            )
            self.session.add(user)
        await self.session.commit()
    
    async def add_bookmark(self, user_id: int):
        user = await self.session.get(User, user_id)
        stmt = select(Bookmark).where(and_(Bookmark.user_id == user_id, Bookmark.page == user.page))
        res = await self.session.execute(stmt)
        res = res.first()

        if not res:
            bookmark = Bookmark(
                user_id=user_id,
                page=user.page
            )
            self.session.add(bookmark)
        await self.session.commit()

    async def get_user_data(self, id: int) -> User:
        user = await self.session.get(User, id)
        return user

    async def update_user_data(self, id: int, page: int) -> User:
        user = await self.session.get(User, id)
        user.page = page

        await self.session.commit()
        return user

    async def delete_bookmark(self, user_id: int, page: int):
        stmt = delete(Bookmark).where(
            and_(user_id == Bookmark.user_id, page == Bookmark.page)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_all_bookmarks(self, user_id) -> List[int]:
        stmt = select(Bookmark.page).where(Bookmark.user_id == user_id)
        result = await self.session.execute(stmt)
        result = [i[0] for i in result.all()]
        return result
        


