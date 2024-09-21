import math
import os

import django
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football.settings')
django.setup()

from django.db.models import Q
from django.utils import timezone

from core.models import Tournament, Round, Rating

import config


async def main_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.row(types.InlineKeyboardButton(text='Рейтинг игроков', callback_data=f'ratings_1'))
    keyboard.row(types.InlineKeyboardButton(text='Сделать прогноз', callback_data=f'tournaments_1'))
    keyboard.row(types.InlineKeyboardButton(text='Мои прогнозы', callback_data=f'predicts_1'))
    keyboard.row(types.InlineKeyboardButton(text='Правила', callback_data=f'rules'))

    return keyboard.as_markup()


async def subscribe_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.row(types.InlineKeyboardButton(text='Перейти и подписаться', url=config.CHANNEL_LINK))
    keyboard.row(types.InlineKeyboardButton(text='Проверить', callback_data='check'))

    return keyboard.as_markup()


async def tournaments_keyboard(page):
    keyboard = InlineKeyboardBuilder()

    tournaments = await sync_to_async(Tournament.objects.filter(is_active=True).all)()
    tournaments_count = await sync_to_async(len)(tournaments)
    pages_count = math.ceil(tournaments_count / config.PER_PAGE)
    tournaments = tournaments[(page - 1) * config.PER_PAGE:page * config.PER_PAGE]
    for tournament in tournaments:
        symbol = '⏳'
        if tournament.finished:
            symbol = '✅'
        keyboard.row(types.InlineKeyboardButton(text=f'{symbol} {tournament.title}', callback_data=f'tournament_1_{tournament.pk}'))
    
    nav = []
    if pages_count >= 2:
        if page == 1:
            nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'nothing'))
        else:
            nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'tournaments_{page - 1}'))
        nav.append(types.InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
        if page == pages_count:
            nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'nothing'))
        else:
            nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'tournaments_{page + 1}'))
    keyboard.row(*nav)
    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_main'))

    return keyboard.as_markup()


async def rounds_keyboard(page, tournament_id):
    keyboard = InlineKeyboardBuilder()

    tournament = await sync_to_async(Tournament.objects.filter(id=tournament_id).first)()
    if tournament:
        rounds = await sync_to_async(tournament.rounds.all)()
        rounds_count = await sync_to_async(len)(rounds)
        pages_count = math.ceil(rounds_count / config.PER_PAGE)
        rounds = rounds[(page - 1) * config.PER_PAGE:page * config.PER_PAGE]
        for round in rounds:
            symbol = '⏳'
            if round.finished:
                symbol = '✅'
            keyboard.row(types.InlineKeyboardButton(text=f'{symbol} {round.title}', callback_data=f'round_1_{round.pk}'))
    
        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'tournament_{page - 1}_{tournament_id}'))
            nav.append(types.InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'tournament_{page + 1}_{tournament_id}'))
        keyboard.row(*nav)

    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_tournaments'))

    return keyboard.as_markup()


async def matches_keyboard(page, round_id,):
    keyboard = InlineKeyboardBuilder()

    round = await sync_to_async(Round.objects.filter(id=round_id).first)()
    if round:
        matches = await sync_to_async(round.matches.all)()
        matches_count = await sync_to_async(len)(matches)
        pages_count = math.ceil(matches_count / config.PER_PAGE)
        matches = matches[(page - 1) * config.PER_PAGE:page * config.PER_PAGE]
        for match in matches:
            symbol = '⏳'
            if timezone.localtime(match.date) <= timezone.now():
                symbol = '✅'

            if isinstance(match.score1, int) and isinstance(match.score2, int):
                button_text = f'{symbol} {match.team1} {match.score1}:{match.score2} {match.team2}'
            else:
                button_text = f'{symbol} {match.team1} - {match.team2}'

            keyboard.row(types.InlineKeyboardButton(text=button_text, callback_data=f'match_{match.pk}_m'))
    
        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'round_{page - 1}_{round_id}'))
            nav.append(types.InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'round_{page + 1}_{round_id}'))
        keyboard.row(*nav)

    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_rounds_{round_id}'))

    return keyboard.as_markup()


async def match_keyboard(match_date, score1, score2, team1, team2, match_id, label='m'):
    keyboard = InlineKeyboardBuilder()

    if match_date >= timezone.now():
        keyboard.row(types.InlineKeyboardButton(text=team1, callback_data=f'nothing'))
        team1_nav = []
        if score1 == 0:
            team1_nav.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
        else:
            team1_nav.append(types.InlineKeyboardButton(text='-', callback_data=f'minus_1_{match_id}_{score1}_{score2}_{label}'))
        
        team1_nav.append(types.InlineKeyboardButton(text=str(score1), callback_data=f'nothing'))
        team1_nav.append(types.InlineKeyboardButton(text='+', callback_data=f'plus_1_{match_id}_{score1}_{score2}_{label}'))
        keyboard.row(*team1_nav)

        keyboard.row(types.InlineKeyboardButton(text=team2, callback_data=f'nothing'))
        team2_nav = []
        if score2 == 0:
            team2_nav.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
        else:
            team2_nav.append(types.InlineKeyboardButton(text='-', callback_data=f'minus_2_{match_id}_{score1}_{score2}_{label}'))
        
        team2_nav.append(types.InlineKeyboardButton(text=str(score2), callback_data=f'nothing'))
        team2_nav.append(types.InlineKeyboardButton(text='+', callback_data=f'plus_2_{match_id}_{score1}_{score2}_{label}'))
        keyboard.row(*team2_nav)
        keyboard.row(types.InlineKeyboardButton(text='Подтвердить', callback_data=f'confirm_{match_id}_{score1}_{score2}'))

    if label == 'm':
        keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_matches_{match_id}'))
    else:
        keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_predicts_{match_id}'))

    return keyboard.as_markup()


async def predicts_keyboard(page, predicts, tournament_id):
    keyboard = InlineKeyboardBuilder()

    predicts_count = await sync_to_async(len)(predicts)
    if predicts_count:
        pages_count = math.ceil(predicts_count / config.PER_PAGE)
        predicts = predicts[(page - 1) * config.PER_PAGE_PREDICTS:page * config.PER_PAGE_PREDICTS]
        for predict in predicts:
            symbol = '⏳'
            if predict.points is not None:
                symbol = '✅'

            match = await sync_to_async(lambda: predict.match)()
            button_text = f'{symbol} {match.team1} {predict.score1}:{predict.score2} {match.team2}'

            keyboard.row(types.InlineKeyboardButton(text=button_text, callback_data=f'match_{match.pk}_p'))
    
        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'tpredicts_{page - 1}'))
            nav.append(types.InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'tpredicts_{page + 1}'))
        keyboard.row(*nav)

    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_roundsp_{tournament_id}'))

    return keyboard.as_markup()


async def ratings_keyboard(page, user):
    keyboard = InlineKeyboardBuilder()

    ratings = await sync_to_async(Rating.objects.filter(is_active=True).all)()
    ratings_count = await sync_to_async(len)(ratings)
    pages_count = math.ceil(ratings_count / config.PER_PAGE)
    ratings = ratings[(page - 1) * config.PER_PAGE:page * config.PER_PAGE]
    for rating in ratings:
        symbol = ''
        if await sync_to_async(rating.has_user_predicts)(user):
            symbol = '👁 '
        keyboard.row(types.InlineKeyboardButton(text=f'{symbol}{rating.title}', callback_data=f'rating_{rating.pk}'))
    
    nav = []
    if pages_count >= 2:
        if page == 1:
            nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'nothing'))
        else:
            nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'ratings_{page - 1}'))
        nav.append(types.InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
        if page == pages_count:
            nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'nothing'))
        else:
            nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'ratings_{page + 1}'))
    keyboard.row(*nav)
    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_main'))

    return keyboard.as_markup()


async def back_ratings_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_ratings'))

    return keyboard.as_markup()


async def back_main_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_main'))

    return keyboard.as_markup()


async def tournaments_predicts_keyboard(page, user):
    keyboard = InlineKeyboardBuilder()

    tournaments = await sync_to_async(Tournament.objects.filter(Q(is_active=True) &
                                                                Q(rounds__matches__match_predicts__user=user)).all)()
    tournaments_count = await sync_to_async(len)(tournaments)
    pages_count = math.ceil(tournaments_count / config.PER_PAGE)
    tournaments = tournaments[(page - 1) * config.PER_PAGE:page * config.PER_PAGE]
    for tournament in tournaments:
        symbol = '⏳'
        if tournament.finished:
            symbol = '✅'
        keyboard.row(types.InlineKeyboardButton(text=f'{symbol} {tournament.title}', callback_data=f'tournamentp_1_{tournament.pk}'))
    
    nav = []
    if pages_count >= 2:
        if page == 1:
            nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'nothing'))
        else:
            nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'predicts_{page - 1}'))
        nav.append(types.InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
        if page == pages_count:
            nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'nothing'))
        else:
            nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'predicts_{page + 1}'))
    keyboard.row(*nav)
    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_main'))

    return keyboard.as_markup()


async def rounds_predicts_keyboard(page, tournament_id, user):
    keyboard = InlineKeyboardBuilder()

    tournament = await sync_to_async(Tournament.objects.filter(id=tournament_id).first)()
    if tournament:
        rounds = await sync_to_async(tournament.rounds.filter(matches__match_predicts__user=user).all)()
        rounds_count = await sync_to_async(len)(rounds)
        pages_count = math.ceil(rounds_count / config.PER_PAGE)
        rounds = rounds[(page - 1) * config.PER_PAGE:page * config.PER_PAGE]
        for round in rounds:
            symbol = '⏳'
            if round.finished:
                symbol = '✅'
            keyboard.row(types.InlineKeyboardButton(text=f'{symbol} {round.title}', callback_data=f'roundp_1_{round.pk}'))
    
        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'<<', callback_data=f'tournamentp_{page - 1}_{tournament_id}'))
            nav.append(types.InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'nothing'))
            else:
                nav.append(types.InlineKeyboardButton(text=f'>>', callback_data=f'tournamentp_{page + 1}_{tournament_id}'))
        keyboard.row(*nav)

    keyboard.row(types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_tournamentsp'))

    return keyboard.as_markup()
    