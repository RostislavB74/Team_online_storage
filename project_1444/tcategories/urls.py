from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tcategories.views import TCategoriesViewSet

router = DefaultRouter()


router.register(r"tcategories", TCategoriesViewSet, basename="tcategories")


urlpatterns = [
    path("", include(router.urls)),
]
