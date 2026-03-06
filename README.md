# AI QA Agent

AI-powered agent for API testing.

## Test reports

[Github Pages](https://xofxela.github.io/ai_qa_agent/)

## API Testing Example

To test an API, use the scripts below:

### REST
```bash
python -m src.main --protocol rest --spec examples/openapi.json --base-url https://petstore.swagger.io/v2
```

### GraphQL
```bash
python -m src.main --protocol graphql --spec https://spacex-production.up.railway.app/ --base-url https://spacex-production.up.railway.app/
```

### gRPC
```bash
python -m src.main --protocol grpc --base-url grpcb.in:9000
```
