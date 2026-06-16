from django.contrib import admin

from .models import Fragment, Story


class FragmentInline(admin.TabularInline):
    """Fragmentos de solo lectura: el orden secuencial lo gestiona el juego."""

    model = Fragment
    extra = 0
    readonly_fields = ('order', 'author', 'text', 'created_at')
    fields = ('order', 'author', 'text', 'created_at')
    ordering = ('order',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'visibility', 'status', 'created_at')
    list_filter = ('status', 'visibility')
    search_fields = ('title', 'creator__email')
    readonly_fields = ('slug', 'created_at')
    inlines = [FragmentInline]
