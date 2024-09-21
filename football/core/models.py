from django.db import models
from django.db.models import Q, Sum, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class TGUser(models.Model):
    user_id = models.CharField(verbose_name='Телеграм id', max_length=100, unique=True)
    username = models.CharField(verbose_name='Ник телеграм', max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name='Имя', max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Создание аккаунта', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Последнее обновление', auto_now=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('-created_at',)

    def __str__(self):
        if self.username:
            return self.username
        
        return self.user_id


class Tournament(models.Model):
    title = models.CharField(verbose_name='Название чемпионата', max_length=200, unique=True)
    is_active = models.BooleanField(verbose_name='активен', default=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0, null=True, blank=True,)
    finished = models.BooleanField(verbose_name='Завершен', default=False)

    class Meta:
        verbose_name = 'чемпионат'
        verbose_name_plural = 'чемпионаты'
        ordering = ('order',)

    def __str__(self):
        return self.title


class Round(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='rounds', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Название тура', max_length=200)
    finished = models.BooleanField(verbose_name='Завершен', default=False)

    class Meta:
        verbose_name = 'тур'
        verbose_name_plural = 'туры'
    
    def __str__(self):
        return f'{self.tournament.title} ({self.title})'


class Match(models.Model):
    round = models.ForeignKey(Round, related_name='matches', on_delete=models.CASCADE)
    team1 = models.CharField(verbose_name='Команда 1', max_length=50)
    team2 = models.CharField(verbose_name='Команда 2', max_length=50)
    score1 = models.IntegerField(verbose_name='Счет 1', blank=True, null=True, default=None,)
    score2 = models.IntegerField(verbose_name='Счет 2', blank=True, null=True, default=None,)
    date = models.DateTimeField(verbose_name='Время проведения', help_text='Московское время')

    class Meta:
        verbose_name = 'матч'
        verbose_name_plural = 'матчи'
        ordering = ('date',)
    
    def __str__(self):
        return f'{self.team1} - {self.team2}'
    
    def result(self):
        if self.score1 > self.score2:
            return 'win'
        
        if self.score1 == self.score2:
            return 'draw'
        
        if self.score1 < self.score2:
            return 'lose'
    
    def difference(self):
        return self.score1 - self.score2


class Predict(models.Model):
    user = models.ForeignKey(TGUser, related_name='predicts', on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name='match_predicts', on_delete=models.CASCADE)
    score1 = models.IntegerField(verbose_name='Счет 1', blank=True, null=True,)
    score2 = models.IntegerField(verbose_name='Счет 2', blank=True, null=True,)
    created_at = models.DateTimeField(verbose_name='Создание прогноза', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновление прогноза', auto_now=True)
    points = models.IntegerField(verbose_name='Баллы', blank=True, null=True, default=None,)

    class Meta:
        verbose_name = 'матч'
        verbose_name_plural = 'матчи'
        ordering = ('-updated_at',)
    
    def __str__(self):
        return f'{self.match.team1} - {self.match.team2}'
    
    def _result(self):
        if self.score1 > self.score2:
            return 'win'
        
        if self.score1 == self.score2:
            return 'draw'
        
        if self.score1 < self.score2:
            return 'lose'
    
    def _difference(self):
        return self.score1 - self.score2
    
    def calculate_points(self):
        if self.score1 == self.match.score1 and self.score2 == self.match.score2:
            self.points = 5
        
        elif self._result() == self.match.result() and self._difference() == self.match.difference():
            self.points = 3
        
        elif self._result() == self.match.result():
            self.points = 2

        else:
            self.points = 0
        
        self.save()


class Rating(models.Model):
    title = models.CharField(verbose_name='Название рейтинга', max_length=200, unique=True)
    rounds = models.ManyToManyField(Round, verbose_name='Туры в рейтинге')
    is_active = models.BooleanField(verbose_name='активен', default=True)
    order = models.PositiveIntegerField(verbose_name='Порядок', default=0, null=True, blank=True,)

    class Meta:
        verbose_name = 'рейтинг'
        verbose_name_plural = 'рейтинги'
        ordering = ('order',)

    def __str__(self):
        return self.title
    
    def has_user_predicts(self, user: TGUser):
        for round in self.rounds.all():
            matches = round.matches.all()
            for match in matches:
                if Predict.objects.filter(Q(points__isnull=False) & Q(user=user) & Q(match=match)).exists():
                    return True

        return False
    
    def get_leaderboard(self):
        return TGUser.objects.filter(predicts__match__round__in=self.rounds.all()) \
            .annotate(total_points=Sum('predicts__points'),
                      non_zero_predicts_count=Count('predicts__points', filter=Q(predicts__points__gt=0))) \
            .order_by('-total_points', 'non_zero_predicts_count')
    

@receiver(post_save, sender=Match)
def update_delivery_valid(sender, instance, **kwargs):
    if instance.score1 is not None and instance.score2 is not None:
        for predict in instance.match_predicts.all():
            predict.calculate_points()


@receiver(post_save, sender=Match)
def check_if_round_finished(sender, instance, **kwargs):
    pass
    if instance.round.matches.filter(date__gte=timezone.now()).exists():
        instance.round.finished = False
        instance.round.save()
    else:
        instance.round.finished = True
        instance.round.save()


@receiver(post_save, sender=Round)
def check_if_tournament_finished(sender, instance, **kwargs):
    pass
    if instance.tournament.rounds.filter(finished=False).exists():
        instance.tournament.finished = False
        instance.tournament.save()
    else:
        instance.tournament.finished = True
        instance.tournament.save()