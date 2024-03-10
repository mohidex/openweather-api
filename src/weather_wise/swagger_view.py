import yaml
from django.conf import settings
from django.http import JsonResponse


async def swagger_json(request):
    with open(settings.SWEGGER_DOCS_PATH, 'r') as yaml_file:
        openapi_spec = yaml.safe_load(yaml_file)
    return JsonResponse(openapi_spec)
