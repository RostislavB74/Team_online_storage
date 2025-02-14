"""
URL configuration for project_1444 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path
# from django.conf import settings
# from django.conf.urls.static import static
# urlpatterns = [
#     path('admin/', admin.site.urls),   
#  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT), 
#  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
# ]
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from product.views import ProductAPIList, ProductAPIUpdate 
from product.views import RingSizeLookup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/v1/auth/', include('rest_framework.urls')),
    path('api/v1/product/', ProductAPIList.as_view()),
     path('api/v1/product/<int:pk>/', ProductAPIUpdate.as_view()),
    # path('api/', include('product.urls')),
    path('api/v1/ringsize/', RingSizeLookup.as_view(), name='product-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)