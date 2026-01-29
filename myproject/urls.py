from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls), # Disabled default admin to use custom admin
    path('', include('main.urls')),
]
