from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import get_user_available_discounts

class AvailableDiscountsView(APIView):
    def get(self, request):
        discounts = get_user_available_discounts(request.user)
        data = [
            {
                "id": d.id,
                "name": d.name,
                "percent": d.discount_percent,
                "valid_to": d.valid_to
            }
            for d in discounts
        ]
        return Response(data)