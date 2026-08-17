from django.contrib import admin
from .models import Translation, FavoriteTranslation


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'source_language_name', 'target_language_name', 'short_source', 'character_count', 'created_at']
    list_filter   = ['source_language', 'target_language', 'created_at']
    search_fields = ['source_text', 'translated_text', 'user__username']
    readonly_fields = ['character_count', 'created_at']
    date_hierarchy  = 'created_at'
    ordering        = ['-created_at']

    def short_source(self, obj):
        return obj.source_text[:60] + '...' if len(obj.source_text) > 60 else obj.source_text
    short_source.short_description = 'Source Text'


@admin.register(FavoriteTranslation)
class FavoriteTranslationAdmin(admin.ModelAdmin):
    list_display  = ['id', 'translation', 'label', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['translation__source_text', 'label']
    ordering      = ['-created_at']