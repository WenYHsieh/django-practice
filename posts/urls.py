from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='post-list'),
    path('/<int:pk>', views.PostDetail.as_view(), name='post-detail'),
    path('/send-email', views.SendEmailTest.as_view(), name='send-email'),
]
