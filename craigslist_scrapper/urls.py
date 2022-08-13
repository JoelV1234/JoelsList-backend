from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_postings', views.get_postings),
    path('suggestions', views.get_search_suggestion)
]