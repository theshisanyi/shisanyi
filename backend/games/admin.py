from django.contrib import admin
from .models import Game, Category, SimilarGame

class SimilarGameInline(admin.TabularInline):
    model = SimilarGame
    fk_name = 'game'
    extra = 3

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [SimilarGameInline]
    list_display = ['title', 'rating', 'is_hot', 'sort_weight', 'release_date', 'play_duration']
    list_filter = ['categories', 'is_hot']
    search_fields = ['title']
    fieldsets = (
        (None, {
            'fields': ('title', 'cover_image', 'categories')
        }),
        ('评分与信息', {
            'fields': ('rating', 'play_duration', 'release_date', 'purchase_link')
        }),
        ('内容', {
            'fields': ('official_intro', 'review')
        }),
        ('展示设置', {
            'fields': ('is_hot', 'sort_weight')
        }),
    )
