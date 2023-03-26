from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('documents/', views.documents, name='documents'),
    path('documents/<int:sid>/<str:title>', views.paper, name='paper'),
    path('testing/', views.testing, name='testing'),
    path('logout/',views.userLogout,name='logout')
]
