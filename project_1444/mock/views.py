import json
from pathlib import Path

from django.conf import settings
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseBadRequest
from django.utils.http import http_date
from django.views import View


class MockViewApiV0(View):
    mock_path = settings.STATIC_ROOT / "mock"

    def get(self, request):
        try:
            if request.path.endswith("/"):
                request_path = Path(request.path.lstrip("/"))
                request_path = request_path / request_path.name
            else:
                request_path = Path(request.path.lstrip("/"))

            # Security check. Check if inside, if wrong then exception
            context_path = (self.mock_path / request_path).resolve()  # resolve path
            context_path.relative_to(self.mock_path)

            if not context_path.exists():
                return HttpResponseNotFound("Not found")

            last_modified_datetime = context_path.stat().st_mtime  # get last modified
            last_modified_datetime = http_date(last_modified_datetime)

            with context_path.open("r", encoding="utf-8") as f:
                context = json.load(f)

            response = JsonResponse(
                context,
                safe=False,
                json_dumps_params={"ensure_ascii": False},
            )
            response["Last-Modified"] = last_modified_datetime
            # print(last_modified_datetime)
            return response
        except ValueError:
            return HttpResponseBadRequest("Invalid path (path traversal attempt)")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")
        except OSError:
            return HttpResponseBadRequest("Error reading file")
