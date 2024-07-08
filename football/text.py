import os
import django

from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football.settings')
django.setup()

from django.utils import timezone
import config

start_text = 'Привет!\nC помощью этого бота ты сможешь соревноваться в точности своих футбольных прогнозов!'
subscribe_needed = f'📰 Условием данного бота является подписка на [канал]({config.CHANNEL_LINK}).'
menu_text = '⚽️ Меню:'
no_subscribe = 'Вы не подписаны на канал, попробуйте еще раз.'
tournaments_text = '🥅 Футбольные чемпионаты:'
predicts_text = 'Прогнозы на счет матча:'
ratings_text = 'Рейтинги участников:'

async def match_description(match, predict):
    round = await sync_to_async(lambda: match.round.title)()
    tournament = await sync_to_async(lambda: match.round.tournament.title)()

    match_date = timezone.localtime(match.date).strftime('%d.%m.%Y %H:%M')
    reply_text = f'*{match_date}\n\n{tournament}\n{round}:*\n'
    if match.score1 is not None and match.score2 is not None:
        reply_text += f'*{match.team1}* {match.score1}:{match.score2} *{match.team2}*'
    else:
        reply_text += f'{match.team1} - {match.team2}'

    if predict:
        if timezone.localtime(match.date) <= timezone.now():
            predict_title = '\n\nВаш прогноз'
        else:
            predict_title = '\n\nТекущий прогноз'

        predict_block =f'*{predict_title}:*\n*{match.team1}* {predict.score1}:{predict.score2} *{match.team2}*'
        if predict.points is not None:
            predict_block += f'\n*Очки:* {predict.points}'
        
        reply_text += predict_block
    
    if timezone.localtime(match.date) >= timezone.now():
        if predict:
            reply_text += '\n\n*Изменить прогноз:*'
        else:
            reply_text += '\n\n*Сделать прогноз:*'
    
    return reply_text


async def leaderboard(title, leaderboard, user_place, user):
    reply_text = f'*{title}:*\n'
    for num, leader in enumerate(leaderboard[:10]):
        total_points = leader.total_points
        if total_points is None:
            total_points = 0
        if user_place and num + 1 == user_place:
            reply_text += f'\n*{num + 1}. {leader.name}: {total_points} б.*'
        else:
            reply_text += f'\n*{num + 1}.* {leader.name}: *{total_points} б.*'
        
        if user.user_id == config.MANAGER_ID:
            reply_text += leader.user_id
    
    if user_place and user_place > 10:
        user_name = leaderboard[user_place - 1].name
        total_points = leaderboard[user_place - 1].total_points
        if total_points is None:
            total_points = 0
        reply_text += f'\n\n...\n*{user_place}.* {user_name}: *{total_points} б.*\n...'
    elif not user_place:
        reply_text += f'\n\n...\n*Вы еще не приняли участия в данном рейтинге.'

    return reply_text

rules = '''
    1\.  Конкурс прогнозов – это игра, в которой фанаты футбола могут попробовать свои силы в предсказывании результатов матчей ⚽️\
    \nИгра является бесплатной и несёт развлекательных характер, где есть возможность выиграть призы 🎁\
    \n2\.  Оставить прогнозы могут только пользователи, подписанные на [канал]({config.CHANNEL_LINK}) 📱\
    \n3\.  Основное меню состоит из следующих пунктов:\
    \n– __Рейтинг игроков__ 🔝\
    \n– __Сделать прогноз__ 🎲\
    \n– __Мои прогнозы__ 📙\
    \n– __Правила__ ✅️\
    \n4\.  Прогноз на матч можно сделать не позднее, чем за 1 минуту до начала матча ⏰\
    \n5\.  На каждый матч участник может сделать только один прогноз\.  До начала матча возможно изменить свой прогноз ⌛\
    \n6\.  Очки начисляются следующим образом:\
    \n–  за точно угаданный счёт – 5 очков\
    \n–  за угаданный исход и разницу мячей – 3 очка\
    \n–  за угаданный исход – 2 очка\
    \n7\.  Учитывается итоговый счёт основного времени матча ⏱\
    \n8\.  В случае равенства ⚖️ очков у двух и более участников приоритетность мест в рейтинге определяется следующим образом:\
    \n–  по наибольшему числу угаданных точных результатов\
    \n–  по наибольшему числу угаданных исходов и разниц мячей\
    \n–  по наибольшему числу угаданных исходов\
    \n9\.  Перед проведением конкурса определяется формат турнира, количество призовых мест и подарки, которые получат победители 🎁\
    \n10\.  Администраторы «Футбольного подкаста» оставляют за собой право решать спорные ситуации 🤝\
'''