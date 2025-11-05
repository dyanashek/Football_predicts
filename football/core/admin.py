import nested_admin
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from adminsortable2.admin import SortableAdminMixin
from reversion.admin import VersionAdmin

from core.models import TGUser, Tournament, Round, Match, Predict, Rating, BaseSettings


class PredictInline(admin.TabularInline):
    model = Predict
    extra = 0
    fields = ('match', 'score1', 'score2', 'points', 'created_at', 'updated_at')
    readonly_fields = ('match', 'match__round', 'match__round__tournament', 'score1', 'score2', 'points', 'created_at', 'updated_at')


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
    fields = ('user_id', 'username', 'name')
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
    

@admin.register(BaseSettings)
class BaseSettingsAdmin(VersionAdmin):
    list_display = ('__str__',)
    
    def has_add_permission(self, request):
        if BaseSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        settings, _ = BaseSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse('admin:core_basesettings_change', args=[settings.id])
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "Редактирование настроек"
        return super().change_view(request, object_id, form_url, extra_context)

