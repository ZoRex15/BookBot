from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from app.filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from app.keyboards.bookmarks_kb import (create_bookmarks_keyboard,
                                    create_edit_keyboard)
from app.keyboards.pagination_kb import create_pagination_keyboard
from app.lexicon import LEXICON
from app.services.file_handling import book

from app.database import Database

router = Router()


# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@router.message(CommandStart())
async def process_start_command(message: Message, db: Database):
    await message.answer(LEXICON[message.text])
    await db.add_user(
        id=message.from_user.id
    )


# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


# Этот хэндлер будет срабатывать на команду "/beginning"
# и отправлять пользователю первую страницу книги с кнопками пагинации
@router.message(Command(commands='beginning'))
async def process_beginning_command(message: Message, db: Database):
    await db.update_user_data(
        id=message.from_user.id,
        page=1
    )
    user = await db.get_user_data(id=message.from_user.id)
    text = book[user.page]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{user.page}/{len(book)}',
            'forward'
        )
    )


# Этот хэндлер будет срабатывать на команду "/continue"
# и отправлять пользователю страницу книги, на которой пользователь
# остановился в процессе взаимодействия с ботом
@router.message(Command(commands='continue'))
async def process_continue_command(message: Message, db: Database):
    user = await db.get_user_data(id=message.from_user.id)
    text = book[user.page]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{user.page}/{len(book)}',
            'forward'
        )
    )


# Этот хэндлер будет срабатывать на команду "/bookmarks"
# и отправлять пользователю список сохраненных закладок,
# если они есть или сообщение о том, что закладок нет
@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message, db: Database):
    bookmarks = await db.get_all_bookmarks(user_id=message.from_user.id)
    if bookmarks:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *bookmarks
            )
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'forward')
async def process_forward_press(callback: CallbackQuery, db: Database):
    user = await db.get_user_data(id=callback.from_user.id)
    if user.page < len(book):
        user = await db.update_user_data(
            id=callback.from_user.id,
            page=user.page + 1
        )
        text = book[user.page]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{user.page}/{len(book)}',
                'forward'
            )
        )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'backward')
async def process_backward_press(callback: CallbackQuery, db: Database):
    user = await db.get_user_data(id=callback.from_user.id)
    if user.page > 1:
        user = await db.update_user_data(
            id=callback.from_user.id,
            page=user.page - 1
        )
        text = book[user.page]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{user.page}/{len(book)}',
                'forward'
            )
        )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с номером текущей страницы и добавлять текущую страницу в закладки
@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
async def process_page_press(callback: CallbackQuery, db: Database):
    await db.add_bookmark(
        user_id=callback.from_user.id
    )
    await callback.answer('Страница добавлена в закладки!')


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок
@router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery, db: Database):
    text = book[int(callback.data)]
    user = await db.update_user_data(
        id=callback.from_user.id,
        page=int(callback.data)
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{user.page}/{len(book)}',
            'forward'
        )
    )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "редактировать" под списком закладок
@router.callback_query(F.data == 'edit_bookmarks')
async def process_edit_press(callback: CallbackQuery, db: Database):
    bookmarks = await db.get_all_bookmarks(
        user_id=callback.from_user.id
    )
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *bookmarks
        )
    )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "отменить" во время работы со списком закладок (просмотр и редактирование)
@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок к удалению
@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery, db: Database):
    await db.delete_bookmark(
        user_id=callback.from_user.id,
        page=int(callback.data[:-3])
    )
    bookmarks = await db.get_all_bookmarks(
        user_id=callback.from_user.id
    )
    if bookmarks:
        await callback.message.edit_text(
            text=LEXICON['/bookmarks'],
            reply_markup=create_edit_keyboard(
                *bookmarks
            )
        )
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
    await callback.answer()