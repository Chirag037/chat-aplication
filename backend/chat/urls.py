from django.urls import path
# pyrefly: ignore [missing-import]
from . import views
# pyrefly: ignore [missing-import]
from .views import moderate_user

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('api/moderate-user/', moderate_user),


]