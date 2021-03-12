from rest_framework import serializers # allows you to send data from database through api to client
from django.db.models import Sum # this allows you to add together data
from .models import Recipe, Ingredient, Upvote
from django.contrib.auth.models import User

class RecipeSerializer(serializers.ModelSerializer): # allows you to create serializers that correspond with models
    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all()) # primarykeyrelatedfield represents the target of this and finds them using primary key, this is a many to many field and queryset is where you obtain the data from
    total_calories = serializers.SerializerMethodField() # calls serializer metod on class it's attached to
    upvotes = serializers.SerializerMethodField()

    def get_total_calories(self, recipe):
        return Ingredient.objects.filter(recipe=recipe).aggregate(Sum('calories')) # filters all ingredients by recipe then adds them together
    
    def get_upvotes(self, recipe):
        return Upvote.objects.filter(recipe=recipe).count()

    class Meta: # tells what fields you want to take and what models
        model = Recipe
        fields = ('id', 'author', 'title', 'image', 'time_mins', 'ingredients', 'total_calories', 'diet', 'upvotes', 'created', 'updated')
        read_only_fields = ('id', 'author')

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'calories')
        read_only_fields = ('id',) # you need to add a comma to make this a tuple because str isn't allowed


class UpvoteSerializer(serializers.ModelSerializer):
    class Meta: # this allows you to define permissions, associated data table name i.e. Upvote etc
        model = Upvote
        fields = ('id',)
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True) # allows ingredients to be displayed in the model but not altered

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input type' : 'password'}, write_only=True) # ensures that password won't be seen
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password']) # when a user is created it needs to pass data validation, if it does it is then stored in a list
        user.save() # saves new user
        return user