# AI QA Agent

AI-powered agent for API testing.

## Test reports

[Github Pages](https://xofxela.github.io/ai_qa_agent/)

## REST API Testing Example

To test a REST API, use the Swagger API as an example:
```bash
python -m src.main --protocol rest --spec https://petstore.swagger.io/v2/swagger.json  --base-url https://petstore.swagger.io/v2
```


## GraphQL Testing Example

To test a GraphQL API, use the SpaceX API as an example:

```bash
python -m src.main --protocol graphql --spec https://spacex-production.up.railway.app/ --base-url https://spacex-production.up.railway.app/
```
