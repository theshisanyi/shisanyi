from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class Game(models.Model):
    title = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    play_duration = models.CharField(max_length=50, blank=True)
    release_date = models.DateField(null=True, blank=True)
    official_intro = models.TextField(blank=True)
    review = models.TextField(blank=True)
    purchase_link = models.URLField(blank=True)
    is_hot = models.BooleanField(default=False, db_index=True)
    sort_weight = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-sort_weight', '-created_at']

class SimilarGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='similar_games')
    similar_game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='similar_to')
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
        unique_together = ('game', 'similar_game')

    def __str__(self):
        return f"{self.game.title} \u2192 {self.similar_game.title}"
