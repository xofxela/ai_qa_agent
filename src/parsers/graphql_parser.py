import httpx
from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport
from src.parsers.base import SpecParser
from src.models.graphql import GraphQLArgument, GraphQLField, GraphQLSchema
from src.utils.logger import logger

class GraphQLParser(SpecParser):
    async def parse(self, source: str) -> GraphQLSchema:
        """source: URL GraphQL endpoint for introspection"""
        logger.info(f"Introspecting GraphQL schema from {source}")
        transport = HTTPXAsyncTransport(url=source)
        async with Client(transport=transport, fetch_schema_from_transport=False) as client:
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
                  }
                }
            """)
            result = await client.execute(introspection_query)
            fields = result["__schema"]["queryType"]["fields"]
            parsed_fields = []
            for f in fields:
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
                parsed_fields.append(GraphQLField(
                    name=f["name"],
                    description=f.get("description"),
                    args=args,
                    type=return_type,
                    is_deprecated=f.get("isDeprecated", False)
                ))
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
        # Простой именованный тип
        name = type_info.get("name", "unknown")
        return name, False
