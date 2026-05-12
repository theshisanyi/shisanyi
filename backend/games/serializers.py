from rest_framework import serializers
from .models import Game, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class GameListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = Game
        fields = ['id', 'title', 'cover_image', 'categories', 'rating', 'release_date', 'is_hot', 'sort_weight']

class GameDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    similar_games = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = '__all__'

    def get_similar_games(self, obj):
        qs = obj.similar_games.select_related('similar_game').all()
        return [
            {
                'id': sg.similar_game.id,
                'title': sg.similar_game.title,
                'cover_image': sg.similar_game.cover_image.url if sg.similar_game.cover_image else None,
                'rating': sg.similar_game.rating,
            }
            for sg in qs
        ]
