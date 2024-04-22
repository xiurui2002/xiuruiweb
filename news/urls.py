from django.urls import path

from . import views

urlpatterns = [
    path("login", views.userLogin, name="userLogin"),
    path("logout", views.userLogout, name="userLogout"),
    path("stories", views.manageStory, name="manageStories"),
    path("stories/<int:key>", views.deleteStory, name="deleteStory"),
    path('api/directory', views.for_agency),
]