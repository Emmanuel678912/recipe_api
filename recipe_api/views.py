from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.response import Response  
from .models import Recipe, Ingredient, Upvote
from .serializers import RecipeSerializer, IngredientSerializer, UpvoteSerializer, RecipeDetailSerializer, UserRegistrationSerializer
from django.contrib.auth.models import User

# Create your views here.

class RecipeCreateView(generics.CreateAPIView): # this creates only endpoints (it's a POST method handler meaning that it is used to create or update) - are where APIs can access resources to carry out tasks
    queryset = Recipe.objects.all() # this is where the view accesses it's information in order to create Recipe pages
    serializer_class = RecipeSerializer # only authenticated users can create a recipe
    permission_classes = [permissions.IsAuthenticated] # this ensures that only those authenticated have permission

    def perform_create(self, serializer): 
        serializer.save(author=self.request.user) # ensures that the user who creates this recipe is automatically the author

class RecipeListView(generics.ListAPIView): # this is a GET method handler meaning that it fetches data on recipes, ListAPIView is a read only instance
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permissions_classes = [permissions.AllowAny] # anyone can view the recipes

class IngredientCreateView(generics.ListCreateAPIView): # allows ingredients to be read and created
    queryset = Ingredient.objects.all() # access all ingredient objects
    serializer_class = IngredientSerializer # connect the ingredient serializer to the view

class CreateUpvoteView(generics.CreateAPIView):
    serializer_class = UpvoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): # ensures that the correct user and recipe are displayed when upvoting
        user = self.request.user 
        recipe = Recipe.objects.get(pk=self.kwargs['pk']) # obtains the primary key so that the url is unique
        return Upvote.objects.filter(user=user, recipe=recipe) 

    def perform_create(self, serializer): # allows database to know who upvoted
        if self.get_queryset().exists():
            raise ValidationError('You have already voted on this.')
        user = self.request.user 
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        serializer.save(user=user, recipe=recipe)

class RecipeDetailView(generics.RetrieveAPIView): # allows you to GET data on the recipe
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    permission_classes = [permissions.AllowAny]

class RecipeUpdateView(generics.RetrieveUpdateDestroyAPIView): # this allows you to update and delete recipes
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated] # ensures that only logged in users can update or delete recipes

    def delete(self, request, *args, **kwargs):
        recipe = Recipe.objects.filter(author=self.request.user, pk=kwargs['pk']) # the user can only delete recipes they created
        # pk ensures that the pk is equal to the one in the URL
        if recipe.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError("This isn't your recipe.") # only a user who has access can delete the recipe which means if the recipe doesn't exist in the user's account it can't be destroyed

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data) # this converts the token into JSON format so that it can display when the user registers
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user).key # obtains token as soons as user is saved
            data = {'token' : token}
        else:
            data = serializer.errors # if the user isn't validated raise an error
        return Response(data=data, status=201) # 201 means successful response