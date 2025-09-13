from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from tcategories.models import TCategories
from tcategories.searializers import TCategoriesSerializer
from utils.language_code import get_language_code


class TCategoriesViewSet(viewsets.ModelViewSet):

    serializer_class = TCategoriesSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        lang = get_language_code(self.request)
        qs = TCategories.objects.language(lang)
        if self.action == "list":
            return qs.select_related("translations")
        return qs.all()

    @action(detail=False)
    def get_root(self, request):
        qs = self.get_queryset().filter(parent=None)
        return self.list(request, qs)

    @action(detail=False, kwargs={"parent_id": "int"})
    def get_children(self, request, parent_id=None):
        qs = self.get_queryset().filter(parent_id=parent_id)
        return self.list(request, qs)
