from django.db import models
from rest_framework.authtoken.admin import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name



class Recipe(models.Model):
    name = models.CharField(max_length=30)
    ingredients = models.CharField(max_length=1000)
    cook_time = models.CharField(max_length=20)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    difficulty = models.IntegerField(range(1, 5))
    description = models.TextField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    def __str__(self):
        return self.name




class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ManyToManyField('Recipe')

    def __str__(self):
        return f"{self.user.username}'s Favorites"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='following', blank=True)

    def __str__(self):
        return self.user.username








