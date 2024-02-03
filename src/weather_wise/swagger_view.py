import yaml
from django.conf import settings
from django.http import JsonResponse


async def swagger_json(request):
    api_spec_path = settings.BASE_DIR.joinpath('docs/openapi-spec.yml')
    with open(api_spec_path, 'r') as yaml_file:
        openapi_spec = yaml.safe_load(yaml_file)
    return JsonResponse(openapi_spec)
