from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('submit', views.submit_comment, name='submit'),
    path('detail/<int:pk>', views.MessageDetailView.as_view(), name='detail'),
    path('message/update/<int:pk>', views.MessageUpdateView.as_view(), name='update'),
    path('message/delete/<int:pk>', views.MessageDeleteView.as_view(), name='delete'),
    path('signup/', views.SignUpView.as_view(), name='signup')
]
