from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.views.generic import TemplateView
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Category
from .serializers import *
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.authtoken.admin import User
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect, JsonResponse
from rest_framework import filters





# Create your views here.

######################################Login##########################################################
class SignupView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(username=request.data['username'])
            token, created = Token.objects.get_or_create(user=user)
            response.data['token'] = token.key

            send_verification_email(user, request)
            UserProfile.objects.create(user=user)
        return response
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the user's token and delete it
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Successfully logged out'})
class MyProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Your view logic here
        return Response({'message': 'This is a protected view'})
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Mark user as verified (You can set a flag in your User model)
        user.is_verified = True
        user.save()
        login_url = reverse('login') + '?verified=true'
        return JsonResponse({'message': 'Email verification successful, return to login page and login'})
    else:
        return render(request, 'verification_failed.html')
def send_verification_email(user,request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    verification_link = f"{domain}/verify/{uid}/{token}/"

    subject = 'Verify Your Email'
    message = render_to_string('verification_email.txt', {'user': user, 'verification_link': verification_link})
    send_mail(subject, message, 'authenticate636@gmail.com', [user.email])
def send_verification_email_again(request):
    email = request.POST.get('email')
    user = get_object_or_404(User, email=email)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    verification_link = f"{domain}/verify/{uid}/{token}/"

    subject = 'Verify Your Email'
    message = render_to_string('verification_email.txt', {'user': user, 'verification_link': verification_link})
    send_mail(subject, message, 'authenticate636@gmail.com', [user.email])



######################################Recipies##########################################################


class CategoriesView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class AllRecipiesView(ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavoriteListView(APIView):
    authentication_classes = [TokenAuthentication]  # Add TokenAuthentication
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        favorite_recipes = Favorite.objects.filter(user=user)
        serializer = FavoriteSerializer(favorite_recipes, many=True)
        return Response(serializer.data)


class RecipesByCategoryView(ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        category_name = self.kwargs['category_name']
        category = get_object_or_404(Category, name=category_name)
        return Recipe.objects.filter(category=category)


class RecipeDetailView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_object(self):
        name = self.kwargs.get('name')
        return get_object_or_404(Recipe, name=name)


class AddRecipeView(generics.CreateAPIView):
    serializer_class = RecipeSerializer
    ###authentication_classes = [TokenAuthentication]
    ####permission_classes = [IsAuthenticated]


class UserProfileView(APIView):
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        followers = user_profile.followers.all()

        # Corrected variable name
        following_users = request.user.following.all()

        user_recipes = Recipe.objects.filter(author=request.user)

        serializer = UserProfileSerializer(user_profile, context={'followers': followers, 'following': following_users})
        recipe_serializer = RecipeSerializer(user_recipes, many=True)
        data = {
            'profile': serializer.data,
            'recipes': recipe_serializer.data
        }
        return Response(data)


class FollowUserView(APIView):
    def post(self, request, username):
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.follow(user_to_follow)

        return Response({"success": f"Now following {username}"}, status=status.HTTP_200_OK)


class UserProfileDetailView(APIView):
    def get(self, request, username):
        try:
            # Retrieve the user profile for the requested user
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response({"message": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve followers and following for the requested user
        followers = user_profile.followers.all()
        following = user_profile.user.following.all()

        user_recipes = Recipe.objects.filter(author=user_profile.user)
        recipe_serializer = RecipeSerializer(user_recipes, many=True)
        serializer = UserProfileSerializer(user_profile, context={'followers': followers, 'following': following})


        data = {
            'profile': serializer.data,
            'recipes': recipe_serializer.data
        }
        return Response(data)





class RecipeSearchView(generics.ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'ingredients', 'description']

