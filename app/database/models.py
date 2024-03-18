from app.database.base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from typing import List


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    page: Mapped[int] = mapped_column(nullable=False, default=1)

    bookmarks: Mapped[List['Bookmark']] = relationship('Bookmark',
                                                        cascade='all, delete, delete-orphan',
                                                        back_populates='user'
                                                        )

    def __repr__(self):
        return f'UserModel(id={self.id!r}, page={self.page!r})'

class Bookmark(Base):
    __tablename__ = 'Bookmarks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id = mapped_column(ForeignKey('Users.id'))
    page: Mapped[int] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(back_populates='bookmarks')

    def __repr__(self):
        return f'BookmarkModel(id={self.id!r}, page={self.page!r}, user_id={self.user_id!r})'
