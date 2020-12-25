from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="index"),
    path("songs/", views.songs, name="songs"),
    path("songs/<int:id>", views.songpost, name="songpost"),
    path("login", views.user_login, name="login"),
    path("signup", views.signup, name="signup"),
    path("c/<str:channel>", views.channel, name="channel"),
    path("upload", views.upload, name="upload"),
    path("logout_user", views.logout_user, name="logout_user"),
    path('history', views.history, name='history'),
    path('watchlater', views.watchlater, name='watchlater'),
    path('history', views.history, name='history'),
    path('search',views.search, name='search'),
    path('like/<int:pk>',views.LikeView,name='like_song')
]
