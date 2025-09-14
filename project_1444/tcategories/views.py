import logging

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from tcategories.models import TCategories
from tcategories.searializers import TCategoriesSerializer, TCategoryFullPathSerializer

logger = logging.getLogger(__name__)


@extend_schema(tags=["Categories"])
class TCategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TCategories.objects.all()
    serializer_class = TCategoriesSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        logger.debug("get_queryset: %s", self.action)
        match self.action:
            case "get_only_root":
                return self.queryset.filter(parent__isnull=True)
            case "get_only_children":
                return self.queryset.filter(parent__isnull=False)
        return self.queryset

    def get_serializer_class(self):
        logger.debug("get_serializer_class: %s", self.action)
        match self.action:
            case "get_children" | "retrieve":
                return TCategoryFullPathSerializer
        return self.serializer_class

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

    @extend_schema(
        methods=["get"],
        parameters=[
            OpenApiParameter(
                "parent_id",
                OpenApiTypes.INT,
                OpenApiParameter.PATH,  # This is the key change
                description="The ID of the parent category",
                required=True,
            ),
            OpenApiParameter(
                "include_children",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Whether to include nested children in the response",
                required=False,
                default=False,
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="(?P<parent_id>[0-9]+)/children",
        description="Get child categories for a specific parent category",
    )
    def get_children(self, request, parent_id=None):
        try:
            include_children = (
                request.query_params.get("include_children", "false").lower() == "true"
            )

            def get_recursive_children(parent_id):
                direct_children = self.get_queryset().filter(parent_id=parent_id)
                if not include_children:
                    return self.get_serializer(direct_children, many=True).data
                result = []
                for child in direct_children:
                    child_data = self.get_serializer(child).data
                    nested_children = get_recursive_children(child.id)
                    if nested_children:
                        child_data["children"] = nested_children
                    result.append(child_data)
                return result

            children = get_recursive_children(parent_id)
            return Response(children)
        except ValueError:
            return Response(
                {"error": "Invalid parent_id format"},
                status=status.HTTP_400_BAD_REQUEST,
            )
