from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiExample

TCATEGORIES_GET_CHILDREN_PARAMETERS = [
    OpenApiParameter(
        "include_children",
        OpenApiTypes.BOOL,
        OpenApiParameter.QUERY,
        description="Whether to include nested children in the response",
        required=False,
        default=False,
    )
]

# Define the two response examples
RESPONSE_EXAMPLE_WITHOUT_CHILDREN = OpenApiExample(
    "Response without nested children",
    description="Example of a response when include_children is False",
    value=[
        {
            "id": 101,
            "name": "Child Category 1",
            "parent_id": 123,
        },
        {"id": 102, "name": "Child Category 2", "parent_id": 123, "children": []},
    ],
    response_only=True,
)

RESPONSE_EXAMPLE_WITH_CHILDREN = OpenApiExample(
    "Response with nested children",
    description="Example of a response when include_children is True",
    value=[
        {
            "id": 101,
            "name": "Child Category 1",
            "parent_id": 123,
            "children": [
                {"id": 201, "name": "Grandchild Category 1", "parent_id": 101}
            ],
        },
        {"id": 102, "name": "Child Category 2", "parent_id": 123, "children": []},
    ],
    response_only=True,
)
