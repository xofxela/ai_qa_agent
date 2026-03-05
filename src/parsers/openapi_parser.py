import json
from typing import List, Dict, Any
from src.parsers.base import SpecParser
from src.models.endpoint import ApiEndpoint, HttpMethod, ParameterLocation, EndpointParameter
from src.utils.http_client import HttpClient
from src.utils.logger import logger

class OpenApiParser(SpecParser):
    async def parse(self, source: str) -> List[ApiEndpoint]:
        """Parse OpenAPI spec from URL or local file."""
        spec = await self._load_spec(source)
        endpoints = []
        
        # Determine OpenAPI version
        swagger_version = spec.get("swagger")  # for 2.0
        openapi_version = spec.get("openapi")  # for 3.x
        
        if swagger_version:
            logger.info(f"Parsing Swagger {swagger_version} spec")
            endpoints = self._parse_swagger_v2(spec)
        elif openapi_version:
            logger.info(f"Parsing OpenAPI {openapi_version} spec")
            endpoints = self._parse_openapi_v3(spec)
        else:
            raise ValueError("Unknown OpenAPI version")
        
        return endpoints
    
    async def _load_spec(self, source: str) -> Dict[str, Any]:
        if source.startswith(('http://', 'https://')):
            async with HttpClient() as client:
                resp = await client.get(source)
                return resp.json()
        else:
            with open(source, 'r') as f:
                return json.load(f)
    
    def _parse_swagger_v2(self, spec: dict) -> List[ApiEndpoint]:
        """Парсит Swagger 2.0 спецификацию"""
        endpoints = []
        base_path = spec.get("basePath", "")
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            full_path = base_path + path
            
            for method, operation in path_item.items():
                if method not in ["get", "post", "put", "delete", "patch"]:
                    continue
                    
                # Парсим параметры
                endpoint_params = []
                parameters = operation.get("parameters", [])
                
                for param in parameters:
                    # Определяем location
                    param_in = param.get("in", "query")
                    if param_in == "path":
                        location = ParameterLocation.PATH
                    elif param_in == "query":
                        location = ParameterLocation.QUERY
                    elif param_in == "header":
                        location = ParameterLocation.HEADER
                    elif param_in == "body":
                        location = ParameterLocation.BODY
                    elif param_in == "formData":
                        location = ParameterLocation.FORM
                    else:
                        continue
                    
                    # Для body-параметров схема может быть вложенной
                    param_schema = {}
                    if "schema" in param:
                        param_schema = param["schema"]
                    elif "type" in param:
                        # Для простых параметров создаём схему на лету
                        param_schema = {
                            "type": param["type"],
                            "format": param.get("format"),
                            "items": param.get("items"),
                            "enum": param.get("enum")
                        }
                    
                    endpoint_params.append(EndpointParameter(
                        name=param["name"],
                        location=location,
                        required=param.get("required", False),
                        param_schema=param_schema,
                        description=param.get("description")
                    ))
                
                # Парсим security
                security = operation.get("security", [])
                
                # Создаём эндпоинт
                endpoint = ApiEndpoint(
                    path=full_path,
                    method=HttpMethod(method.upper()),
                    operation_id=operation.get("operationId"),
                    summary=operation.get("summary"),
                    parameters=endpoint_params,
                    responses=operation.get("responses", {}),
                    security=security
                )
                endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_openapi_v3(self, spec: Dict) -> List[ApiEndpoint]:
        # TODO: implement OpenAPI 3.x parsing
        logger.warning("OpenAPI 3.x parsing not fully implemented yet, using fallback.")
        # Simplified fallback
        return self._parse_swagger_v2(spec)  # temporary
