from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from core.models import Rating, BaseSettings, TGUser, Predict


class LeadersboardView(TemplateView):
    template_name = 'leadersboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ratings']  = Rating.objects.filter(is_active=True)
        
        if rating_id := self.request.GET.get('rating_id'):
            rating = Rating.objects.filter(id=rating_id, is_active=True).first() or Rating.objects.filter(is_active=True).first()
        else:
            rating = Rating.objects.filter(is_active=True).first()
        
        if rating:
            base_settings = BaseSettings.objects.first()
            context['curr_rating'] = rating
            context['leaderboard'] = rating.get_leaderboard()[:base_settings.leaders_per_page]

        return context


@require_http_methods(["GET"])
def get_player_details(request, rating_id, player_id):
    """
    API endpoint для получения деталей игрока: имя, telegram ID, очки и список матчей с прогнозами
    """
    try:
        rating = Rating.objects.get(id=rating_id, is_active=True)
        player = TGUser.objects.get(id=player_id)
    except (Rating.DoesNotExist, TGUser.DoesNotExist):
        return JsonResponse({'error': 'Рейтинг или игрок не найден'}, status=404)
    
    # Получаем все прогнозы игрока для этого рейтинга
    predicts = Predict.objects.filter(
        user=player,
        match__round__in=rating.rounds.all(),
        points__isnull=False
    ).select_related('match', 'match__round').order_by('match__date')
    
    # Формируем список матчей
    matches_data = []
    total_points = 0
    
    for predict in predicts:
        match = predict.match
        matches_data.append({
            'date': match.date.strftime('%d.%m.%Y'),
            'round': match.round.title,
            'team1': match.team1,
            'team2': match.team2,
            'score': f"{match.score1}:{match.score2}" if match.score1 is not None and match.score2 is not None else "-",
            'prediction': f"{predict.score1}:{predict.score2}" if predict.score1 is not None and predict.score2 is not None else "-",
            'points': predict.points if predict.points is not None else 0
        })
        total_points += predict.points if predict.points is not None else 0
    
    # Формируем ответ
    response_data = {
        'id': player.id,
        'name': player.name or 'Неизвестно',
        'tg': player.user_id,
        'points': total_points,
        'matches': matches_data
    }
    
    return JsonResponse(response_data)


class YandexView(TemplateView):
    template_name = 'yandex_9c9cb277299ce48e.html'