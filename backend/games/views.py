from rest_framework import viewsets, filters
from .models import Game, Category
from .serializers import GameListSerializer, GameDetailSerializer, CategorySerializer

class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all().prefetch_related('categories')
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['release_date', 'sort_weight', 'rating']
    ordering = ['-sort_weight', '-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return GameListSerializer
        return GameDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'retrieve':
            qs = qs.prefetch_related('similar_games__similar_game')
        category = self.request.query_params.get('category')
        is_hot = self.request.query_params.get('is_hot', '')
        if category:
            qs = qs.filter(categories__slug=category)
        if is_hot.lower() == 'true':
            qs = qs.filter(is_hot=True)[:5]
        return qs

    def paginate_queryset(self, queryset):
        is_hot = self.request.query_params.get('is_hot', '')
        if is_hot.lower() == 'true':
            return None
        return super().paginate_queryset(queryset)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
