from rest_framework import viewsets
from .models import Product
from .serializers import (
    RingSizeSerializer,
)

class RingSizeViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = RingSizeSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RingSizeSerializer
        return super().get_serializer_class()
