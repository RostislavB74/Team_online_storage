import logging

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from project_1444.settings import LANGUAGE_CODE
from tcategories.models import TCategories
from tcategories.openapi_spec import (
    TCATEGORIES_GET_CHILDREN_PARAMETERS,
)
from tcategories.searializers import TCategoriesSerializer, TCategoryFullPathSerializer
from utils.language_code import get_language_code

logger = logging.getLogger(__name__)


@extend_schema(tags=["Categories"])
class TCategoriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TCategories.objects.all()
    serializer_class = TCategoriesSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        lang = get_language_code(self.request) or LANGUAGE_CODE
        logger.debug("get_queryset: %s %s", self.action, lang)
        queryset = self.queryset.language(lang)
        match self.action:
            case "get_only_root":
                return queryset.filter(parent__isnull=True)
            case "get_only_children":
                return queryset.filter(parent__isnull=False)
        return queryset

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
        parameters=TCATEGORIES_GET_CHILDREN_PARAMETERS,
        operation_id="tcategories_children_get",
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
