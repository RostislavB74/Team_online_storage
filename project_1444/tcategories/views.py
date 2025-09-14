from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from tcategories.models import TCategories
from tcategories.searializers import TCategoriesSerializer


@extend_schema(tags=["Categories"])
class TCategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TCategories.objects.all()
    serializer_class = TCategoriesSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        match self.action:
            case "get_only_root":
                return self.queryset.filter(parent__isnull=True)
            case "get_only_children":
                return self.queryset.filter(parent__isnull=False)

        return self.queryset

    @action(
        detail=False,
        url_path="root",
        methods=["get"],
        description="Get root categories",
    )
    def get_only_root(self, request):
        return self.list(request)

    @action(
        detail=False,
        url_path="children",
        methods=["get"],
        description="Get children categories",
    )
    def get_only_children(self, request):
        return self.list(request)

    @action(
        detail=False,
        methods=["get"],
        url_path="(?P<parent_id>[0-9]+)/children",
        description="Get child categories for a specific parent category",
    )
    def get_children(self, request, parent_id=None):
        try:
            queryset = self.get_queryset().filter(parent_id=parent_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid parent_id format"},
                status=status.HTTP_400_BAD_REQUEST,
            )
