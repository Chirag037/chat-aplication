"""
URL configuration for backend project.
Serves Vue frontend + Django API
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from chat.views import health_check, register, login, messages, list_users, room_list, create_direct_room, list_group_rooms, join_group_room

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/health/', health_check),
    path('api/register/', register),
    path('api/login/', login),
    path('api/messages/', messages),
    path('api/users/', list_users),
    path('api/rooms/', room_list),
    path('api/rooms/direct/', create_direct_room),
    path('api/rooms/group/', list_group_rooms),
    path('api/rooms/join/', join_group_room),
    
    # Serve Vue frontend for all other routes (catch-all)
    path('', TemplateView.as_view(template_name='index.html')),
    path('<path:rest>', TemplateView.as_view(template_name='index.html')),
]

# Serve static files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)