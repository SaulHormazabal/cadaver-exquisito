from django.contrib import admin

from .models import Fragment, Story


class FragmentInline(admin.TabularInline):
    model = Fragment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('order', 'author', 'text', 'created_at')
    ordering = ('order',)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'visibility', 'status', 'created_at')
    list_filter = ('status', 'visibility')
    search_fields = ('title', 'creator__email')
    readonly_fields = ('slug', 'created_at')
    inlines = [FragmentInline]
