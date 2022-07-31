from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_posting', views.get_posting),
    path('suggestions', views.get_search_suggestion)
]