import httpx
from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport
from src.parsers.base import SpecParser
from src.models.graphql import GraphQLArgument, GraphQLField, GraphQLSchema
from src.utils.logger import logger
from typing import Dict, Any, List, Optional

class GraphQLParser(SpecParser):
    async def parse(self, source: str) -> GraphQLSchema:
        """source: URL GraphQL endpoint for introspection"""
        logger.info(f"Introspecting GraphQL schema from {source}")
        transport = HTTPXAsyncTransport(url=source)
        async with Client(transport=transport, fetch_schema_from_transport=False) as client:
            # Расширенный интроспекционный запрос, получающий все типы и их поля
            introspection_query = gql("""
                query IntrospectionQuery {
                  __schema {
                    queryType {
                      fields {
                        name
                        description
                        args {
                          name
                          description
                          type {
                            name
                            kind
                            ofType {
                              name
                              kind
                              ofType {
                                name
                                kind
                                ofType {
                                  name
                                  kind
                                }
                              }
                            }
                          }
                        }
                        type {
                          name
                          kind
                          ofType {
                            name
                            kind
                            ofType {
                              name
                              kind
                              ofType {
                                name
                                kind
                              }
                            }
                          }
                        }
                        isDeprecated
                      }
                    }
                    types {
                      kind
                      name
                      fields {
                        name
                        description
                        args {
                          name
                          description
                          type {
                            name
                            kind
                            ofType {
                              name
                              kind
                              ofType {
                                name
                                kind
                              }
                            }
                          }
                        }
                        type {
                          name
                          kind
                          ofType {
                            name
                            kind
                            ofType {
                              name
                              kind
                            }
                          }
                        }
                        isDeprecated
                      }
                    }
                  }
                }
            """)
            result = await client.execute(introspection_query)
            
            # Строим словарь типов для быстрого доступа
            types_map = {}
            for t in result["__schema"]["types"]:
                if t["name"].startswith("__"):
                    continue  # пропускаем внутренние типы
                types_map[t["name"]] = t
            
            # Парсим поля Query
            fields = result["__schema"]["queryType"]["fields"]
            parsed_fields = []
            for f in fields:
                if f.get("isDeprecated"):
                    continue
                args = []
                for a in f.get("args", []):
                    arg_type, required = self._extract_type_info(a["type"])
                    args.append(GraphQLArgument(
                        name=a["name"],
                        type=arg_type,
                        required=required,
                        description=a.get("description")
                    ))
                return_type, _ = self._extract_type_info(f["type"])
                # Добавляем информацию о полях возвращаемого типа
                field_info = {
                    "name": f["name"],
                    "type": return_type,
                    "args": [a.dict() for a in args],
                    "description": f.get("description"),
                    "fields": self._get_fields_for_type(return_type, types_map)
                }
                parsed_fields.append(field_info)
                
            logger.info(f"Parsed {len(parsed_fields)} GraphQL query fields")
            return GraphQLSchema(query_fields=parsed_fields)

    def _extract_type_info(self, type_info):
        """Рекурсивно извлекает имя типа и является ли он обязательным (non-null)"""
        if type_info is None:
            return "unknown", False
        kind = type_info.get("kind")
        if kind == "NON_NULL":
            inner = type_info.get("ofType")
            if inner is None:
                return "unknown", True
            name, _ = self._extract_type_info(inner)
            return name, True
        if kind == "LIST":
            inner = type_info.get("ofType")
            if inner is None:
                return "[]", False
            inner_name, _ = self._extract_type_info(inner)
            return f"[{inner_name}]", False
        name = type_info.get("name", "unknown")
        return name, False

    def _get_fields_for_type(self, type_name: str, types_map: Dict) -> List[Dict]:
        """Возвращает список полей для указанного типа (если это объектный тип)"""
        if type_name.startswith("[") and type_name.endswith("]"):
            inner = type_name[1:-1]
            return self._get_fields_for_type(inner, types_map)
        if type_name in types_map:
            t = types_map[type_name]
            if t["kind"] == "OBJECT":
                fields = []
                for f in t.get("fields", []):
                    if f.get("isDeprecated"):
                        continue
                    field_type, _ = self._extract_type_info(f["type"])
                    fields.append({
                        "name": f["name"],
                        "type": field_type,
                        "description": f.get("description")
                    })
                return fields
        return []
