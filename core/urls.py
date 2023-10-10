from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name="signup"),
    path('singin', views.singin, name="signin"),
    path('settings', views.settings, name='settings'),
    path('logout', views.logout, name="logout"),
    path('upload', views.upload, name='upload'),
    path('like-post', views.like, name='like-post'),
    path("profile/<str:pk>", views.profile, name="profile"),
    path('follow', views.follow, name="follow"),
    path('search', views.search, name='search'),
]