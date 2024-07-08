import os

import django

import asyncio
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ChatMemberLeft, ChatMemberBanned
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football.settings')
django.setup()

from django.db.models import Q
from django.utils import timezone

from core.models import TGUser, Round, Tournament, Match, Predict, Rating

import config
import keyboards
import utils
import text


bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_message(message: types.Message):
    '''Handles start command.'''

    user_id = str(message.from_user.id)
    username = message.from_user.username
    name = message.from_user.full_name
    if not username:
        username = None

    user, _ = await sync_to_async(TGUser.objects.get_or_create)(user_id=user_id)
    user.username = username
    user.name = await utils.escape_markdown(name)
    await sync_to_async(user.save)()

    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL_ID,
                                user_id=user_id,)
    except:
        member = False
    
    if member:
        if not isinstance(member, ChatMemberLeft) and not isinstance(member, ChatMemberBanned):
            member = True
        else:
            member = False

    if member:
        await bot.send_message(chat_id=user_id,
                            text=text.start_text,
                            reply_markup=await keyboards.main_keyboard(),
                            parse_mode='Markdown',
                            )
    else:
        await bot.send_message(chat_id=user_id,
                            text=text.subscribe_needed,
                            reply_markup=await keyboards.subscribe_keyboard(),
                            parse_mode='Markdown',
                            )


@dp.message(Command("menu"))
async def start_message(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    name = message.from_user.full_name
    if not username:
        username = None

    user, _ = await sync_to_async(TGUser.objects.get_or_create)(user_id=user_id)
    user.username = username
    user.name = await utils.escape_markdown(name)
    await sync_to_async(user.save)()

    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL_ID,
                                user_id=user_id,)
    except:
        member = False
    
    if member:
        if not isinstance(member, ChatMemberLeft) and not isinstance(member, ChatMemberBanned):
            member = True
        else:
            member = False
    
    if member:
        await bot.send_message(chat_id=user_id,
                            text=text.menu_text,
                            reply_markup=await keyboards.main_keyboard(),
                            parse_mode='Markdown',
                            )
    else:
        await bot.send_message(chat_id=user_id,
                            text=text.subscribe_needed,
                            reply_markup=await keyboards.subscribe_keyboard(),
                            parse_mode='Markdown',
                            )


@dp.callback_query()
async def callback_query(call: types.CallbackQuery):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    username = call.from_user.username

    user = await sync_to_async(TGUser.objects.get)(user_id=user_id)

    if username:
        user.username = username
        await sync_to_async(user.save)()

    call_data = call.data.split('_')
    query = call_data[0]

    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL_ID,
                                user_id=user_id,)
    except:
        member = False
    
    if member:
        if not isinstance(member, ChatMemberLeft) and not isinstance(member, ChatMemberBanned):
            member = True
        else:
            member = False
    
    if not member:
        if query == 'check':
            await bot.answer_callback_query(
                                callback_query_id=call.id,
                                text=text.no_subscribe,
                                show_alert=True,
                                )
        else:
            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.subscribe_needed,
                                    parse_mode='Markdown',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.subscribe_keyboard(),
                                            )
    else:
        if query == 'check':
            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.menu_text,
                                    parse_mode='Markdown',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.main_keyboard(),
                                            )

        elif query == 'tournaments':
            page = int(call_data[1])

            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.tournaments_text,
                                    parse_mode='Markdown',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.tournaments_keyboard(page),
                                            )
        
        elif query == 'tournament':
            page = int(call_data[1])
            tournament_id = int(call_data[2])
            tournament = await sync_to_async(Tournament.objects.get)(id=tournament_id)
            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=f'*🏟 {tournament.title}:*',
                                    parse_mode='Markdown',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.rounds_keyboard(page, tournament_id),
                                            )
        
        elif query == 'round':
            page = int(call_data[1])
            round_id = int(call_data[2])
            round = await sync_to_async(Round.objects.get)(id=round_id)
            round_title = round.title
            tournament_title = await sync_to_async(lambda: round.tournament.title)()

            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=f'⚽️ *{tournament_title}\n⚽️ {round_title}:*',
                                    parse_mode='Markdown',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.matches_keyboard(page, round_id),
                                            )
        
        elif query == 'match':
            match_id = int(call_data[1])
            label = call_data[2]
            match = await sync_to_async(Match.objects.get)(id=match_id)
            predict = await sync_to_async(match.match_predicts.filter(user=user).first)()

            predict_score1 = 0
            predict_score2 = 0
            if predict:
                predict_score1 = predict.score1
                predict_score2 = predict.score2

            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text=await text.match_description(match, predict),
                                        parse_mode='Markdown',
                                        )
                
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.match_keyboard(timezone.localtime(match.date), predict_score1, predict_score2, match.team1, match.team2, match.pk, label),
                                            )

        elif query == 'plus':
            team_num = int(call_data[1])
            match_id = int(call_data[2])
            score1 = int(call_data[3])
            score2 = int(call_data[4])
            label = call_data[5]

            if team_num == 1:
                score1 += 1
            else:
                score2 += 1

            match = await sync_to_async(Match.objects.get)(id=match_id)

            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.match_keyboard(timezone.localtime(match.date), score1, score2, match.team1, match.team2, match_id, label),
                                            )

        elif query == 'minus':
            team_num = int(call_data[1])
            match_id = int(call_data[2])
            score1 = int(call_data[3])
            score2 = int(call_data[4])
            label = call_data[5]

            if team_num == 1:
                score1 -= 1
            else:
                score2 -= 1

            match = await sync_to_async(Match.objects.get)(id=match_id)
            match_date = timezone.localtime(match.date)
            team1 = match.team1
            team2 = match.team2

            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.match_keyboard(match_date, score1, score2, team1, team2, match_id, label),
                                            )

        elif query == 'confirm':
            match_id = int(call_data[1])
            score1 = int(call_data[2])
            score2 = int(call_data[3])

            match = await sync_to_async(Match.objects.get)(id=match_id)
            predict, _ = await sync_to_async(Predict.objects.get_or_create)(user=user, match=match)
            predict.score1 = score1
            predict.score2 = score2
            await sync_to_async(predict.save)()

            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text=await text.match_description(match, predict),
                                        parse_mode='Markdown',
                                        )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.match_keyboard(timezone.localtime(match.date), score1, score2, match.team1, match.team2, match.pk),
                                            )

        elif query == 'predicts':
            page = int(call_data[1])

            predicts = await sync_to_async(user.predicts.all)()

            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text=text.predicts_text,
                                        parse_mode='Markdown',
                                        )
                
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.predicts_keyboard(page, predicts),
                                            )

        elif query == 'ratings':
            page = int(call_data[1])
            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.ratings_text,
                                    parse_mode='Markdown',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.ratings_keyboard(page, user),
                                            )
        
        elif query == 'rating':
            rating_id = int(call_data[1])
            rating = await sync_to_async(Rating.objects.get)(id=rating_id)
            leaderboard = await sync_to_async(lambda: list(rating.get_leaderboard()))()

            try:
                user_place = leaderboard.index(user) + 1
            except:
                user_place = False
            
            reply_text = await text.leaderboard(rating.title, leaderboard, user_place, user)

            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=reply_text,
                                    parse_mode='Markdown',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.back_ratings_keyboard(),
                                            )

        elif query == 'rules':
            await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.rules,
                                    parse_mode='MarkdownV2',
                                    )
            
            await bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=await keyboards.back_main_keyboard(),
                                        )

        elif query == 'back':
            destination = call_data[1]

            if destination == 'main':
                await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text=text.menu_text,
                                        parse_mode='Markdown',
                                        )
                
                await bot.edit_message_reply_markup(chat_id=chat_id,
                                                message_id=message_id,
                                                reply_markup=await keyboards.main_keyboard(),
                                                )
            
            elif destination == 'tournaments':
                await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.tournaments_text,
                                    parse_mode='Markdown',
                                    )
            
                await bot.edit_message_reply_markup(chat_id=chat_id,
                                                message_id=message_id,
                                                reply_markup=await keyboards.tournaments_keyboard(1),
                                                )
            
            elif destination == 'rounds':
                round_id = int(call_data[2])
                round = await sync_to_async(Round.objects.get)(id=round_id)
                tournament_id = await sync_to_async(lambda: round.tournament.pk)()
                tournament_title = await sync_to_async(lambda: round.tournament.title)()
                await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=f'*🏟 {tournament_title}:*',
                                    parse_mode='Markdown',
                                    )
            
                await bot.edit_message_reply_markup(chat_id=chat_id,
                                                message_id=message_id,
                                                reply_markup=await keyboards.rounds_keyboard(1, tournament_id),
                                                )

            elif destination == 'matches':
                match_id = int(call_data[2])
                match = await sync_to_async(Match.objects.get)(id=match_id)
                round_id = await sync_to_async(lambda: match.round.pk)()
                round_title = await sync_to_async(lambda: match.round.title)()
                tournament_title = await sync_to_async(lambda: match.round.tournament.title)()

                await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=f'⚽️ *{tournament_title}\n⚽️ {round_title}:*',
                                    parse_mode='Markdown',
                                    )
            
                await bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=await keyboards.matches_keyboard(1, round_id),
                                            )

            elif destination == 'predicts':
                predicts = await sync_to_async(user.predicts.all)()

                await bot.edit_message_text(chat_id=chat_id,
                                            message_id=message_id,
                                            text=text.predicts_text,
                                            parse_mode='Markdown',
                                            )
                    
                await bot.edit_message_reply_markup(chat_id=chat_id,
                                                message_id=message_id,
                                                reply_markup=await keyboards.predicts_keyboard(1, predicts),
                                                )

            elif destination == 'ratings':
                await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text=text.ratings_text,
                                        parse_mode='Markdown',
                                        )
            
                await bot.edit_message_reply_markup(chat_id=chat_id,
                                                message_id=message_id,
                                                reply_markup=await keyboards.ratings_keyboard(1, user),
                                                )

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
