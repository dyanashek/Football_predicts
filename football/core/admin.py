from django.contrib import admin
from core.models import TGUser, Tournament, Round, Match, Predict, Rating
from adminsortable2.admin import SortableAdminBase, SortableAdminMixin, SortableStackedInline, SortableTabularInline
from reversion.admin import VersionAdmin
import nested_admin


class PredictInline(admin.TabularInline):
    model = Predict
    extra = 0
    fields = ('match', 'score1', 'score2', 'points', 'created_at', 'updated_at')
    readonly_fields = ('match', 'score1', 'score2', 'points', 'created_at', 'updated_at')


class MatchInline(nested_admin.NestedTabularInline):
    model = Match
    extra = 0


class RoundInline(nested_admin.NestedTabularInline):
    model = Round
    inlines = (MatchInline,)
    extra = 0


@admin.register(TGUser)
class TGUserAdmin(VersionAdmin):
    list_display = ('user_id', 'created_at', 'username', 'name')
    fields = ('user_id', 'created_at', 'username', 'name')
    search_fields = ('name', 'username', 'user_id',)
    readonly_fields = ('user_id',)
    inlines = (PredictInline,)


@admin.register(Tournament)
class TournamentAdmin(SortableAdminMixin, nested_admin.NestedModelAdmin):
    list_display = ('title', 'is_active', 'order')
    fields = ('title', 'is_active',)
    list_filter = ('is_active',)
    inlines = (RoundInline,)


@admin.register(Match)
class MatchAdmin(VersionAdmin):

    def has_module_permission(self, request):
        return False


@admin.register(Round)
class RoundAdmin(VersionAdmin):
    search_fields = ('title', 'tournament__title',)

    def has_module_permission(self, request):
        return False


@admin.register(Rating)
class RatingAdmin(SortableAdminMixin, VersionAdmin):
    list_display = ('title', 'is_active', 'order',)
    autocomplete_fields = ('rounds',)