from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save # post_save throws a signal after using has been saved and signals are utilities that allows us to associate events with an action
from django.dispatch import receiver # receiver decorator links post save signal to function
from rest_framework.authtoken.models import Token

# Create your models here.

class Recipe(models.Model):
    DIET_CHOICES = [
        ('balanced', 'balanced'),
        ('high-protein', 'high-protein'),
        ('high-fibre', 'high-fibre'),
        ('low-fat', 'low-fat'),
        ('low-carb', 'low-carb'),
        ('low-sodium', 'low-sodium'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE) # foreignkey references the primary key of another table
    # models.CASCADE ensures that if the recipe creator is deleted their recipe will be deleted
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    time_mins = models.PositiveIntegerField()
    ingredients = models.ManyToManyField('Ingredient') # allows you to share ingredients between multiple recipes
    diet = models.CharField(max_length=12, choices=DIET_CHOICES, default='balanced') # creates a drop-down list
    created = models.DateTimeField(auto_now_add=True) # checks when the project was updated
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title # this turns the title into a string

    objects = models.Manager() # prevents linting error

class Ingredient(models.Model): # you can get around the python "not defined error" by passing the class as a string
    name = models.CharField(max_length=255)
    calories = models.PositiveIntegerField()

    def __str__(self):
        return self.name
        
    objects = models.Manager()

class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    objects = models.Manager() # always add this when creating a model

@receiver(post_save, sender=User) 
def create_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)