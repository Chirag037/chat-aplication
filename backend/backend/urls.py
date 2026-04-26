from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView  
from chat.views import health_check, register, login, messages, list_users, room_list, create_direct_room, list_group_rooms, join_group_room, ai_proxy, random_joke, ollama_proxy

urlpatterns = [
    path('api/ai/proxy/', ai_proxy),
    path('api/ai/ollama/', ollama_proxy),
    path('admin/', admin.site.urls),
    path('api/health/', health_check),
    path('api/register/', register),
    path('api/login/', login),
    path('api/messages/', messages),
    path('api/users/', list_users),
    path('api/rooms/', room_list),
    path('api/rooms/direct/', create_direct_room),
    path('api/rooms/group/', list_group_rooms),
    path('api/rooms/join/', join_group_room),
    path('api/jokes/random/', random_joke,name='random_joke'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve Vue for all non-API routes
urlpatterns += [
    re_path(r'^(?!api/|admin/).*', TemplateView.as_view(template_name='index.html')),
]