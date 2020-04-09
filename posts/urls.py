from django.urls import path
from . import views

urlpatterns = [
    path('', views.posts),
    path('findByID', views.post),
    path('update', views.update_post),
    path('bulkCreate', views.bulk_create),
]
