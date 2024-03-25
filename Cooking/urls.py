from django.contrib import admin
from django.urls import path, include
from .views import *




urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('signup/', SignupView.as_view(), name="signup"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('protected/', MyProtectedView.as_view(), name='protected-view'),
    path('verify/<str:uidb64>/<str:token>/', verify_email, name='verify_email'),
    path('send-verification-email-again/', send_verification_email_again, name='send_verification_email_again'),
    #############################################################################################################
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('recipies/', AllRecipiesView.as_view(), name='recipies'),
    path('favorite-dishes/', FavoriteListView.as_view(), name='favorite-dishes'),
    path('recipe-by-category/<str:category_name>/', RecipesByCategoryView.as_view(), name="recipe-by-category"),
    path('recipe-details/<str:name>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('add-recipe/', AddRecipeView.as_view(), name='add-recipe'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('follow/<str:username>/', FollowUserView.as_view(), name='follow_user'),
    path('profiles/<str:username>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('recipes/search/', RecipeSearchView.as_view(), name='recipe-search'),

]