from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # core 앱의 urls.py로 모든 요청을 연결합니다.
    path('', include('core.urls')),
]