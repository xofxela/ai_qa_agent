import pytest
import httpx

# GraphQL Endpoint
GRAPHQL_ENDPOINT = "https://spacex-production.up.railway.app/"

@pytest.fixture
async def graphql_client():
    """
    Fixture that provides an httpx.AsyncClient configured for the SpaceX GraphQL API.
    """
    async with httpx.AsyncClient(base_url=GRAPHQL_ENDPOINT) as client:
        yield client

# --- Single Object Queries ---

@pytest.mark.asyncio
async def test_capsule_query(graphql_client):
    """
    Tests the 'capsule' query.
    """
    query = """
        query {
            capsule(id: "5e2e610207560007072962e4") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_core_query(graphql_client):
    """
    Tests the 'core' query.
    """
    query = """
        query {
            core(id: "5f1a2a2207560007072962e7") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_dragon_query(graphql_client):
    """
    Tests the 'dragon' query.
    """
    query = """
        query {
            dragon(id: "5f1b0e7607560007072962f1") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_history_query(graphql_client):
    """
    Tests the 'history' query.
    """
    query = """
        query {
            history(id: "5eb0e4b40756000707296322") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_landpad_query(graphql_client):
    """
    Tests the 'landpad' query.
    """
    query = """
        query {
            landpad(id: "5e2e610207560007072962e3") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launch_query(graphql_client):
    """
    Tests the 'launch' query.
    """
    query = """
        query {
            launch(id: "5f70006207560007072963e2") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launchpad_query(graphql_client):
    """
    Tests the 'launchpad' query.
    """
    query = """
        query {
            launchpad(id: "5e2e610207560007072962e1") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_payload_query(graphql_client):
    """
    Tests the 'payload' query.
    """
    query = """
        query {
            payload(id: "5f1b0e7607560007072962f1") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_rocket_query(graphql_client):
    """
    Tests the 'rocket' query.
    """
    query = """
        query {
            rocket(id: "falcon9") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_ship_query(graphql_client):
    """
    Tests the 'ship' query.
    """
    query = """
        query {
            ship(id: "61e8966346037f001773726f") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_users_by_pk_query(graphql_client):
    """
    Tests the 'users_by_pk' query.
    """
    query = """
        query {
            users_by_pk(id: "1") {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

# --- List Queries ---

@pytest.mark.asyncio
async def test_capsules_query(graphql_client):
    """
    Tests the 'capsules' query.
    """
    query = """
        query {
            capsules(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_capsules_past_query(graphql_client):
    """
    Tests the 'capsulesPast' query.
    """
    query = """
        query {
            capsulesPast(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_capsules_upcoming_query(graphql_client):
    """
    Tests the 'capsulesUpcoming' query.
    """
    query = """
        query {
            capsulesUpcoming(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_cores_query(graphql_client):
    """
    Tests the 'cores' query.
    """
    query = """
        query {
            cores(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_cores_past_query(graphql_client):
    """
    Tests the 'coresPast' query.
    """
    query = """
        query {
            coresPast(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_cores_upcoming_query(graphql_client):
    """
    Tests the 'coresUpcoming' query.
    """
    query = """
        query {
            coresUpcoming(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_dragons_query(graphql_client):
    """
    Tests the 'dragons' query.
    """
    query = """
        query {
            dragons(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_histories_query(graphql_client):
    """
    Tests the 'histories' query.
    """
    query = """
        query {
            histories(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_landpads_query(graphql_client):
    """
    Tests the 'landpads' query.
    """
    query = """
        query {
            landpads(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launches_query(graphql_client):
    """
    Tests the 'launches' query.
    """
    query = """
        query {
            launches(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launches_past_query(graphql_client):
    """
    Tests the 'launchesPast' query.
    """
    query = """
        query {
            launchesPast(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launches_upcoming_query(graphql_client):
    """
    Tests the 'launchesUpcoming' query.
    """
    query = """
        query {
            launchesUpcoming(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launchpads_query(graphql_client):
    """
    Tests the 'launchpads' query.
    """
    query = """
        query {
            launchpads(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_payloads_query(graphql_client):
    """
    Tests the 'payloads' query.
    """
    query = """
        query {
            payloads(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_rockets_query(graphql_client):
    """
    Tests the 'rockets' query.
    """
    query = """
        query {
            rockets(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_ships_query(graphql_client):
    """
    Tests the 'ships' query.
    """
    query = """
        query {
            ships(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_users_query(graphql_client):
    """
    Tests the 'users' query.
    """
    query = """
        query {
            users(limit: 5) {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

# --- Result Wrapper Queries ---

@pytest.mark.asyncio
async def test_histories_result_query(graphql_client):
    """
    Tests the 'historiesResult' query.
    """
    query = """
        query {
            historiesResult(limit: 5) {
                data {
                    __typename
                }
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launches_past_result_query(graphql_client):
    """
    Tests the 'launchesPastResult' query.
    """
    query = """
        query {
            launchesPastResult(limit: 5) {
                data {
                    __typename
                }
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_rockets_result_query(graphql_client):
    """
    Tests the 'rocketsResult' query.
    """
    query = """
        query {
            rocketsResult(limit: 5) {
                data {
                    __typename
                }
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_ships_result_query(graphql_client):
    """
    Tests the 'shipsResult' query.
    """
    query = """
        query {
            shipsResult(limit: 5) {
                data {
                    __typename
                }
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_users_aggregate_query(graphql_client):
    """
    Tests the 'users_aggregate' query.
    """
    query = """
        query {
            users_aggregate {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

# --- Other Queries ---

@pytest.mark.asyncio
async def test_company_query(graphql_client):
    """
    Tests the 'company' query.
    """
    query = """
        query {
            company {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launch_latest_query(graphql_client):
    """
    Tests the 'launchLatest' query.
    """
    query = """
        query {
            launchLatest {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_launch_next_query(graphql_client):
    """
    Tests the 'launchNext' query.
    """
    query = """
        query {
            launchNext {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_roadster_query(graphql_client):
    """
    Tests the 'roadster' query.
    """
    query = """
        query {
            roadster {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test__service_query(graphql_client):
    """
    Tests the '_service' query.
    """
    query = """
        query {
            _service {
                __typename
            }
        }
    """
    response = await graphql_client.post("", json={"query": query})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"