import pytest
from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport
from datetime import datetime

# GraphQL Endpoint
GRAPHQL_ENDPOINT = "https://spacex-production.up.railway.app/"

@pytest.fixture
async def graphql_client():
    """
    Provides an async GraphQL client instance for testing.
    """
    transport = HTTPXAsyncTransport(url=GRAPHQL_ENDPOINT)
    async with Client(transport=transport, fetch_schema_from_transport=False) as client:
        yield client

# --- Tests for Queries ---

@pytest.mark.asyncio
async def test_capsule_query(graphql_client):
    """
    Tests the 'capsule' query with a valid ID.
    """
    query = gql("""
        query GetCapsule($id: ID!) {
            capsule(id: $id) {
                id
                missions {
                    name
                    flight
                }
                landings
                status
                type
                original_launch
            }
        }
    """)
    # Realistic test data: Using a known capsule ID
    variables = {"id": "5fe3a4795b572c0005c52098"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "capsule" in result
    capsule_data = result["capsule"]
    assert capsule_data is not None, "Capsule data should not be None"

    assert "id" in capsule_data
    assert isinstance(capsule_data["id"], str)
    assert capsule_data["id"] == variables["id"]

    assert "missions" in capsule_data
    assert isinstance(capsule_data["missions"], list)
    if capsule_data["missions"]:
        assert "name" in capsule_data["missions"][0]
        assert isinstance(capsule_data["missions"][0]["name"], str)
        assert "flight" in capsule_data["missions"][0]
        assert isinstance(capsule_data["missions"][0]["flight"], int)

    assert "landings" in capsule_data
    assert isinstance(capsule_data["landings"], int)

    assert "status" in capsule_data
    assert isinstance(capsule_data["status"], str)

    assert "type" in capsule_data
    assert isinstance(capsule_data["type"], str)

    assert "original_launch" in capsule_data
    assert isinstance(capsule_data["original_launch"], str)
    # Optionally, parse and check date format
    try:
        datetime.fromisoformat(capsule_data["original_launch"].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail("original_launch is not a valid ISO format date string")

@pytest.mark.asyncio
async def test_capsules_query(graphql_client):
    """
    Tests the 'capsules' query with limit and sort arguments.
    """
    query = gql("""
        query GetCapsules($limit: Int, $sort: String, $order: String) {
            capsules(limit: $limit, sort: $sort, order: $order) {
                id
                type
                status
            }
        }
    """)
    variables = {"limit": 2, "sort": "original_launch", "order": "desc"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "capsules" in result
    capsules_data = result["capsules"]
    assert isinstance(capsules_data, list)
    assert len(capsules_data) <= variables["limit"]

    for capsule in capsules_data:
        assert "id" in capsule
        assert isinstance(capsule["id"], str)
        assert "type" in capsule
        assert isinstance(capsule["type"], str)
        assert "status" in capsule
        assert isinstance(capsule["status"], str)

@pytest.mark.asyncio
async def test_capsules_past_query(graphql_client):
    """
    Tests the 'capsulesPast' query with a find argument.
    """
    query = gql("""
        query GetPastCapsules($find: CapsulesFind) {
            capsulesPast(find: $find) {
                id
                type
                missions {
                    name
                }
            }
        }
    """)
    variables = {"find": {"type": "Dragon 1.0"}}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "capsulesPast" in result
    past_capsules = result["capsulesPast"]
    assert isinstance(past_capsules, list)

    for capsule in past_capsules:
        assert "id" in capsule
        assert isinstance(capsule["id"], str)
        assert "type" in capsule
        assert isinstance(capsule["type"], str)
        assert capsule["type"] == variables["find"]["type"]
        assert "missions" in capsule
        assert isinstance(capsule["missions"], list)
        if capsule["missions"]:
            assert "name" in capsule["missions"][0]
            assert isinstance(capsule["missions"][0]["name"], str)

@pytest.mark.asyncio
async def test_capsules_upcoming_query(graphql_client):
    """
    Tests the 'capsulesUpcoming' query.
    """
    query = gql("""
        query GetUpcomingCapsules {
            capsulesUpcoming {
                id
                status
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "capsulesUpcoming" in result
    upcoming_capsules = result["capsulesUpcoming"]
    assert isinstance(upcoming_capsules, list)

    for capsule in upcoming_capsules:
        assert "id" in capsule
        assert isinstance(capsule["id"], str)
        assert "status" in capsule
        assert isinstance(capsule["status"], str)

@pytest.mark.asyncio
async def test_company_query(graphql_client):
    """
    Tests the 'company' query.
    """
    query = gql("""
        query {
            company {
                name
                ceo
                founder
                founded
                employees
                launch_sites
                valuation
                links {
                    website
                    flickr
                    twitter
                    elon_twitter
                }
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "company" in result
    company_data = result["company"]
    assert company_data is not None

    assert "name" in company_data
    assert isinstance(company_data["name"], str)

    assert "ceo" in company_data
    assert isinstance(company_data["ceo"], str)

    assert "founder" in company_data
    assert isinstance(company_data["founder"], str)

    assert "founded" in company_data
    assert isinstance(company_data["founded"], int)

    assert "employees" in company_data
    assert isinstance(company_data["employees"], int)

    assert "launch_sites" in company_data
    assert isinstance(company_data["launch_sites"], int)

    assert "valuation" in company_data
    assert isinstance(company_data["valuation"], int)

    assert "links" in company_data
    assert isinstance(company_data["links"], dict)
    assert "website" in company_data["links"]
    assert isinstance(company_data["links"]["website"], str)

@pytest.mark.asyncio
async def test_core_query(graphql_client):
    """
    Tests the 'core' query with a valid ID.
    """
    query = gql("""
        query GetCore($id: ID!) {
            core(id: $id) {
                id
                status
                original_launch
                missions {
                    name
                    flight
                }
                reuse_count
            }
        }
    """)
    # Realistic test data: Using a known core ID
    variables = {"id": "5f7000000000000000000000"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "core" in result
    core_data = result["core"]
    assert core_data is not None

    assert "id" in core_data
    assert isinstance(core_data["id"], str)
    assert core_data["id"] == variables["id"]

    assert "status" in core_data
    assert isinstance(core_data["status"], str)

    assert "original_launch" in core_data
    assert isinstance(core_data["original_launch"], str)

    assert "missions" in core_data
    assert isinstance(core_data["missions"], list)
    if core_data["missions"]:
        assert "name" in core_data["missions"][0]
        assert isinstance(core_data["missions"][0]["name"], str)
        assert "flight" in core_data["missions"][0]
        assert isinstance(core_data["missions"][0]["flight"], int)

    assert "reuse_count" in core_data
    assert isinstance(core_data["reuse_count"], int)

@pytest.mark.asyncio
async def test_cores_query(graphql_client):
    """
    Tests the 'cores' query with limit and find arguments.
    """
    query = gql("""
        query GetCores($limit: Int, $find: CoresFind) {
            cores(limit: $limit, find: $find) {
                id
                status
                serial
            }
        }
    """)
    variables = {"limit": 3, "find": {"status": "active"}}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "cores" in result
    cores_data = result["cores"]
    assert isinstance(cores_data, list)
    assert len(cores_data) <= variables["limit"]

    for core in cores_data:
        assert "id" in core
        assert isinstance(core["id"], str)
        assert "status" in core
        assert isinstance(core["status"], str)
        assert core["status"] == variables["find"]["status"]
        assert "serial" in core
        assert isinstance(core["serial"], str)

@pytest.mark.asyncio
async def test_cores_past_query(graphql_client):
    """
    Tests the 'coresPast' query.
    """
    query = gql("""
        query GetPastCores {
            coresPast {
                id
                serial
                reuse_count
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "coresPast" in result
    past_cores = result["coresPast"]
    assert isinstance(past_cores, list)

    for core in past_cores:
        assert "id" in core
        assert isinstance(core["id"], str)
        assert "serial" in core
        assert isinstance(core["serial"], str)
        assert "reuse_count" in core
        assert isinstance(core["reuse_count"], int)

@pytest.mark.asyncio
async def test_cores_upcoming_query(graphql_client):
    """
    Tests the 'coresUpcoming' query.
    """
    query = gql("""
        query GetUpcomingCores {
            coresUpcoming {
                id
                serial
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "coresUpcoming" in result
    upcoming_cores = result["coresUpcoming"]
    assert isinstance(upcoming_cores, list)

    for core in upcoming_cores:
        assert "id" in core
        assert isinstance(core["id"], str)
        assert "serial" in core
        assert isinstance(core["serial"], str)

@pytest.mark.asyncio
async def test_dragon_query(graphql_client):
    """
    Tests the 'dragon' query with a valid ID.
    """
    query = gql("""
        query GetDragon($id: ID!) {
            dragon(id: $id) {
                id
                name
                type
                first_flight
                active
                crew_capacity
                dry_mass_kg
            }
        }
    """)
    # Realistic test data: Using a known dragon ID
    variables = {"id": "5f7000000000000000000001"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "dragon" in result
    dragon_data = result["dragon"]
    assert dragon_data is not None

    assert "id" in dragon_data
    assert isinstance(dragon_data["id"], str)
    assert dragon_data["id"] == variables["id"]

    assert "name" in dragon_data
    assert isinstance(dragon_data["name"], str)

    assert "type" in dragon_data
    assert isinstance(dragon_data["type"], str)

    assert "first_flight" in dragon_data
    assert isinstance(dragon_data["first_flight"], str)

    assert "active" in dragon_data
    assert isinstance(dragon_data["active"], bool)

    assert "crew_capacity" in dragon_data
    assert isinstance(dragon_data["crew_capacity"], int)

    assert "dry_mass_kg" in dragon_data
    assert isinstance(dragon_data["dry_mass_kg"], int)

@pytest.mark.asyncio
async def test_dragons_query(graphql_client):
    """
    Tests the 'dragons' query with limit.
    """
    query = gql("""
        query GetDragons($limit: Int) {
            dragons(limit: $limit) {
                id
                name
                type
            }
        }
    """)
    variables = {"limit": 2}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "dragons" in result
    dragons_data = result["dragons"]
    assert isinstance(dragons_data, list)
    assert len(dragons_data) <= variables["limit"]

    for dragon in dragons_data:
        assert "id" in dragon
        assert isinstance(dragon["id"], str)
        assert "name" in dragon
        assert isinstance(dragon["name"], str)
        assert "type" in dragon
        assert isinstance(dragon["type"], str)

@pytest.mark.asyncio
async def test_histories_query(graphql_client):
    """
    Tests the 'histories' query with limit and sort.
    """
    query = gql("""
        query GetHistories($limit: Int, $sort: String, $order: String) {
            histories(limit: $limit, sort: $sort, order: $order) {
                id
                title
                event_date_utc
            }
        }
    """)
    variables = {"limit": 5, "sort": "event_date_utc", "order": "asc"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "histories" in result
    histories_data = result["histories"]
    assert isinstance(histories_data, list)
    assert len(histories_data) <= variables["limit"]

    for history in histories_data:
        assert "id" in history
        assert isinstance(history["id"], str)
        assert "title" in history
        assert isinstance(history["title"], str)
        assert "event_date_utc" in history
        assert isinstance(history["event_date_utc"], str)

@pytest.mark.asyncio
async def test_histories_result_query(graphql_client):
    """
    Tests the 'historiesResult' query with find and limit.
    """
    query = gql("""
        query GetHistoriesResult($find: HistoryFind, $limit: Int) {
            historiesResult(find: $find, limit: $limit) {
                totalCount
                edges {
                    node {
                        id
                        title
                    }
                }
            }
        }
    """)
    variables = {"find": {"title_contains": "launch"}, "limit": 3}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "historiesResult" in result
    histories_result = result["historiesResult"]
    assert isinstance(histories_result, dict)

    assert "totalCount" in histories_result
    assert isinstance(histories_result["totalCount"], int)

    assert "edges" in histories_result
    assert isinstance(histories_result["edges"], list)
    assert len(histories_result["edges"]) <= variables["limit"]

    if histories_result["edges"]:
        edge = histories_result["edges"][0]
        assert "node" in edge
        assert isinstance(edge["node"], dict)
        assert "id" in edge["node"]
        assert isinstance(edge["node"]["id"], str)
        assert "title" in edge["node"]
        assert isinstance(edge["node"]["title"], str)

@pytest.mark.asyncio
async def test_history_query(graphql_client):
    """
    Tests the 'history' query with a valid ID.
    """
    query = gql("""
        query GetHistory($id: ID!) {
            history(id: $id) {
                id
                title
                details
                event_date_utc
            }
        }
    """)
    # Realistic test data: Using a known history ID
    variables = {"id": "5eb0e0e4f3cc170006230001"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "history" in result
    history_data = result["history"]
    assert history_data is not None

    assert "id" in history_data
    assert isinstance(history_data["id"], str)
    assert history_data["id"] == variables["id"]

    assert "title" in history_data
    assert isinstance(history_data["title"], str)

    assert "details" in history_data
    assert isinstance(history_data["details"], str)

    assert "event_date_utc" in history_data
    assert isinstance(history_data["event_date_utc"], str)

@pytest.mark.asyncio
async def test_landpad_query(graphql_client):
    """
    Tests the 'landpad' query with a valid ID.
    """
    query = gql("""
        query GetLandpad($id: ID!) {
            landpad(id: $id) {
                id
                name
                full_name
                status
                type
                landing_attempts
                landing_successes
                location {
                    name
                    region
                    latitude
                    longitude
                }
            }
        }
    """)
    # Realistic test data: Using a known landpad ID
    variables = {"id": "5e2e500f5f40c1104934200d"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "landpad" in result
    landpad_data = result["landpad"]
    assert landpad_data is not None

    assert "id" in landpad_data
    assert isinstance(landpad_data["id"], str)
    assert landpad_data["id"] == variables["id"]

    assert "name" in landpad_data
    assert isinstance(landpad_data["name"], str)

    assert "full_name" in landpad_data
    assert isinstance(landpad_data["full_name"], str)

    assert "status" in landpad_data
    assert isinstance(landpad_data["status"], str)

    assert "type" in landpad_data
    assert isinstance(landpad_data["type"], str)

    assert "landing_attempts" in landpad_data
    assert isinstance(landpad_data["landing_attempts"], int)

    assert "landing_successes" in landpad_data
    assert isinstance(landpad_data["landing_successes"], int)

    assert "location" in landpad_data
    assert isinstance(landpad_data["location"], dict)
    assert "name" in landpad_data["location"]
    assert isinstance(landpad_data["location"]["name"], str)

@pytest.mark.asyncio
async def test_landpads_query(graphql_client):
    """
    Tests the 'landpads' query with limit.
    """
    query = gql("""
        query GetLandpads($limit: Int) {
            landpads(limit: $limit) {
                id
                name
                region
            }
        }
    """)
    variables = {"limit": 3}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "landpads" in result
    landpads_data = result["landpads"]
    assert isinstance(landpads_data, list)
    assert len(landpads_data) <= variables["limit"]

    for landpad in landpads_data:
        assert "id" in landpad
        assert isinstance(landpad["id"], str)
        assert "name" in landpad
        assert isinstance(landpad["name"], str)
        assert "region" in landpad
        assert isinstance(landpad["region"], str)

@pytest.mark.asyncio
async def test_launch_query(graphql_client):
    """
    Tests the 'launch' query with a valid ID.
    """
    query = gql("""
        query GetLaunch($id: ID!) {
            launch(id: $id) {
                id
                mission_name
                launch_date_utc
                rocket {
                    rocket_name
                }
                links {
                    article_link
                    video_link
                }
            }
        }
    """)
    # Realistic test data: Using a known launch ID
    variables = {"id": "1"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launch" in result
    launch_data = result["launch"]
    assert launch_data is not None

    assert "id" in launch_data
    assert isinstance(launch_data["id"], str)
    assert launch_data["id"] == variables["id"]

    assert "mission_name" in launch_data
    assert isinstance(launch_data["mission_name"], str)

    assert "launch_date_utc" in launch_data
    assert isinstance(launch_data["launch_date_utc"], str)

    assert "rocket" in launch_data
    assert isinstance(launch_data["rocket"], dict)
    assert "rocket_name" in launch_data["rocket"]
    assert isinstance(launch_data["rocket"]["rocket_name"], str)

    assert "links" in launch_data
    assert isinstance(launch_data["links"], dict)
    assert "article_link" in launch_data["links"]
    assert launch_data["links"]["article_link"] is None or isinstance(launch_data["links"]["article_link"], str)
    assert "video_link" in launch_data["links"]
    assert launch_data["links"]["video_link"] is None or isinstance(launch_data["links"]["video_link"], str)

@pytest.mark.asyncio
async def test_launch_latest_query(graphql_client):
    """
    Tests the 'launchLatest' query.
    """
    query = gql("""
        query GetLatestLaunch {
            launchLatest {
                id
                mission_name
                launch_date_unix
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launchLatest" in result
    latest_launch = result["launchLatest"]
    assert latest_launch is not None

    assert "id" in latest_launch
    assert isinstance(latest_launch["id"], str)

    assert "mission_name" in latest_launch
    assert isinstance(latest_launch["mission_name"], str)

    assert "launch_date_unix" in latest_launch
    assert isinstance(latest_launch["launch_date_unix"], int)

@pytest.mark.asyncio
async def test_launch_next_query(graphql_client):
    """
    Tests the 'launchNext' query.
    """
    query = gql("""
        query GetNextLaunch {
            launchNext {
                id
                mission_name
                upcoming
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launchNext" in result
    next_launch = result["launchNext"]
    assert next_launch is not None

    assert "id" in next_launch
    assert isinstance(next_launch["id"], str)

    assert "mission_name" in next_launch
    assert isinstance(next_launch["mission_name"], str)

    assert "upcoming" in next_launch
    assert isinstance(next_launch["upcoming"], bool)

@pytest.mark.asyncio
async def test_launches_query(graphql_client):
    """
    Tests the 'launches' query with limit and find.
    """
    query = gql("""
        query GetLaunches($limit: Int, $find: LaunchFind) {
            launches(limit: $limit, find: $find) {
                id
                mission_name
                launch_year
            }
        }
    """)
    variables = {"limit": 4, "find": {"launch_year": "2020"}}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launches" in result
    launches_data = result["launches"]
    assert isinstance(launches_data, list)
    assert len(launches_data) <= variables["limit"]

    for launch in launches_data:
        assert "id" in launch
        assert isinstance(launch["id"], str)
        assert "mission_name" in launch
        assert isinstance(launch["mission_name"], str)
        assert "launch_year" in launch
        assert isinstance(launch["launch_year"], str)
        assert launch["launch_year"] == variables["find"]["launch_year"]

@pytest.mark.asyncio
async def test_launches_past_query(graphql_client):
    """
    Tests the 'launchesPast' query with limit and order.
    """
    query = gql("""
        query GetPastLaunches($limit: Int, $order: String) {
            launchesPast(limit: $limit, order: $order) {
                id
                mission_name
                launch_date_local
            }
        }
    """)
    variables = {"limit": 3, "order": "desc"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launchesPast" in result
    past_launches = result["launchesPast"]
    assert isinstance(past_launches, list)
    assert len(past_launches) <= variables["limit"]

    for launch in past_launches:
        assert "id" in launch
        assert isinstance(launch["id"], str)
        assert "mission_name" in launch
        assert isinstance(launch["mission_name"], str)
        assert "launch_date_local" in launch
        assert isinstance(launch["launch_date_local"], str)

@pytest.mark.asyncio
async def test_launches_past_result_query(graphql_client):
    """
    Tests the 'launchesPastResult' query with limit and find.
    """
    query = gql("""
        query GetPastLaunchesResult($limit: Int, $find: LaunchFind) {
            launchesPastResult(limit: $limit, find: $find) {
                result {
                    totalCount
                    edges {
                        node {
                            id
                            mission_name
                        }
                    }
                }
            }
        }
    """)
    variables = {"limit": 2, "find": {"mission_name": "Starlink"}}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launchesPastResult" in result
    launches_past_result = result["launchesPastResult"]
    assert isinstance(launches_past_result, dict)

    assert "result" in launches_past_result
    assert isinstance(launches_past_result["result"], dict)

    result_data = launches_past_result["result"]
    assert "totalCount" in result_data
    assert isinstance(result_data["totalCount"], int)

    assert "edges" in result_data
    assert isinstance(result_data["edges"], list)
    assert len(result_data["edges"]) <= variables["limit"]

    if result_data["edges"]:
        edge = result_data["edges"][0]
        assert "node" in edge
        assert isinstance(edge["node"], dict)
        assert "id" in edge["node"]
        assert isinstance(edge["node"]["id"], str)
        assert "mission_name" in edge["node"]
        assert isinstance(edge["node"]["mission_name"], str)
        assert variables["find"]["mission_name"] in edge["node"]["mission_name"]

@pytest.mark.asyncio
async def test_launches_upcoming_query(graphql_client):
    """
    Tests the 'launchesUpcoming' query with limit.
    """
    query = gql("""
        query GetUpcomingLaunches($limit: Int) {
            launchesUpcoming(limit: $limit) {
                id
                mission_name
                upcoming
            }
        }
    """)
    variables = {"limit": 3}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launchesUpcoming" in result
    upcoming_launches = result["launchesUpcoming"]
    assert isinstance(upcoming_launches, list)
    assert len(upcoming_launches) <= variables["limit"]

    for launch in upcoming_launches:
        assert "id" in launch
        assert isinstance(launch["id"], str)
        assert "mission_name" in launch
        assert isinstance(launch["mission_name"], str)
        assert "upcoming" in launch
        assert isinstance(launch["upcoming"], bool)
        assert launch["upcoming"] is True

@pytest.mark.asyncio
async def test_launchpad_query(graphql_client):
    """
    Tests the 'launchpad' query with a valid ID.
    """
    query = gql("""
        query GetLaunchpad($id: ID!) {
            launchpad(id: $id) {
                id
                name
                full_name
                status
                location {
                    name
                    region
                    latitude
                    longitude
                }
                launch_attempts
                launch_successes
            }
        }
    """)
    # Realistic test data: Using a known launchpad ID
    variables = {"id": "5e2e500f5f40c11049342007"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launchpad" in result
    launchpad_data = result["launchpad"]
    assert launchpad_data is not None

    assert "id" in launchpad_data
    assert isinstance(launchpad_data["id"], str)
    assert launchpad_data["id"] == variables["id"]

    assert "name" in launchpad_data
    assert isinstance(launchpad_data["name"], str)

    assert "full_name" in launchpad_data
    assert isinstance(launchpad_data["full_name"], str)

    assert "status" in launchpad_data
    assert isinstance(launchpad_data["status"], str)

    assert "location" in launchpad_data
    assert isinstance(launchpad_data["location"], dict)
    assert "name" in launchpad_data["location"]
    assert isinstance(launchpad_data["location"]["name"], str)

    assert "launch_attempts" in launchpad_data
    assert isinstance(launchpad_data["launch_attempts"], int)

    assert "launch_successes" in launchpad_data
    assert isinstance(launchpad_data["launch_successes"], int)

@pytest.mark.asyncio
async def test_launchpads_query(graphql_client):
    """
    Tests the 'launchpads' query with limit.
    """
    query = gql("""
        query GetLaunchpads($limit: Int) {
            launchpads(limit: $limit) {
                id
                name
                region
            }
        }
    """)
    variables = {"limit": 3}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "launchpads" in result
    launchpads_data = result["launchpads"]
    assert isinstance(launchpads_data, list)
    assert len(launchpads_data) <= variables["limit"]

    for launchpad in launchpads_data:
        assert "id" in launchpad
        assert isinstance(launchpad["id"], str)
        assert "name" in launchpad
        assert isinstance(launchpad["name"], str)
        assert "region" in launchpad
        assert isinstance(launchpad["region"], str)

@pytest.mark.asyncio
async def test_payload_query(graphql_client):
    """
    Tests the 'payload' query with a valid ID.
    """
    query = gql("""
        query GetPayload($id: ID!) {
            payload(id: $id) {
                id
                type
                name
                manufacturer
                payload_mass_kg
                orbit
            }
        }
    """)
    # Realistic test data: Using a known payload ID
    variables = {"id": "60f600000000000000000000"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "payload" in result
    payload_data = result["payload"]
    assert payload_data is not None

    assert "id" in payload_data
    assert isinstance(payload_data["id"], str)
    assert payload_data["id"] == variables["id"]

    assert "type" in payload_data
    assert isinstance(payload_data["type"], str)

    assert "name" in payload_data
    assert isinstance(payload_data["name"], str)

    assert "manufacturer" in payload_data
    assert isinstance(payload_data["manufacturer"], str)

    assert "payload_mass_kg" in payload_data
    assert isinstance(payload_data["payload_mass_kg"], (int, float))

    assert "orbit" in payload_data
    assert isinstance(payload_data["orbit"], str)

@pytest.mark.asyncio
async def test_payloads_query(graphql_client):
    """
    Tests the 'payloads' query with limit and find.
    """
    query = gql("""
        query GetPayloads($limit: Int, $find: PayloadsFind) {
            payloads(limit: $limit, find: $find) {
                id
                type
                name
                nationality
            }
        }
    """)
    variables = {"limit": 3, "find": {"nationality": "United States"}}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "payloads" in result
    payloads_data = result["payloads"]
    assert isinstance(payloads_data, list)
    assert len(payloads_data) <= variables["limit"]

    for payload in payloads_data:
        assert "id" in payload
        assert isinstance(payload["id"], str)
        assert "type" in payload
        assert isinstance(payload["type"], str)
        assert "name" in payload
        assert isinstance(payload["name"], str)
        assert "nationality" in payload
        assert isinstance(payload["nationality"], str)
        assert payload["nationality"] == variables["find"]["nationality"]

@pytest.mark.asyncio
async def test_roadster_query(graphql_client):
    """
    Tests the 'roadster' query.
    """
    query = gql("""
        query {
            roadster {
                name
                launch_date_utc
                launch_mass_kg
                period_days
                speed_kph
                earth_distance_km
                mars_distance_km
                apoapsis_au
                periapsis_au
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "roadster" in result
    roadster_data = result["roadster"]
    assert roadster_data is not None

    assert "name" in roadster_data
    assert isinstance(roadster_data["name"], str)

    assert "launch_date_utc" in roadster_data
    assert isinstance(roadster_data["launch_date_utc"], str)

    assert "launch_mass_kg" in roadster_data
    assert isinstance(roadster_data["launch_mass_kg"], int)

    assert "period_days" in roadster_data
    assert isinstance(roadster_data["period_days"], float)

    assert "speed_kph" in roadster_data
    assert isinstance(roadster_data["speed_kph"], int)

    assert "earth_distance_km" in roadster_data
    assert isinstance(roadster_data["earth_distance_km"], float)

    assert "mars_distance_km" in roadster_data
    assert isinstance(roadster_data["mars_distance_km"], float)

    assert "apoapsis_au" in roadster_data
    assert isinstance(roadster_data["apoapsis_au"], float)

    assert "periapsis_au" in roadster_data
    assert isinstance(roadster_data["periapsis_au"], float)

@pytest.mark.asyncio
async def test_rocket_query(graphql_client):
    """
    Tests the 'rocket' query with a valid ID.
    """
    query = gql("""
        query GetRocket($id: ID!) {
            rocket(id: $id) {
                id
                name
                type
                company
                country
                height_m
                mass_kg
                first_flight
                description
            }
        }
    """)
    # Realistic test data: Using a known rocket ID
    variables = {"id": "falcon9"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "rocket" in result
    rocket_data = result["rocket"]
    assert rocket_data is not None

    assert "id" in rocket_data
    assert isinstance(rocket_data["id"], str)
    assert rocket_data["id"] == variables["id"]

    assert "name" in rocket_data
    assert isinstance(rocket_data["name"], str)

    assert "type" in rocket_data
    assert isinstance(rocket_data["type"], str)

    assert "company" in rocket_data
    assert isinstance(rocket_data["company"], str)

    assert "country" in rocket_data
    assert isinstance(rocket_data["country"], str)

    assert "height_m" in rocket_data
    assert isinstance(rocket_data["height_m"], float)

    assert "mass_kg" in rocket_data
    assert isinstance(rocket_data["mass_kg"], int)

    assert "first_flight" in rocket_data
    assert isinstance(rocket_data["first_flight"], str)

    assert "description" in rocket_data
    assert isinstance(rocket_data["description"], str)

@pytest.mark.asyncio
async def test_rockets_query(graphql_client):
    """
    Tests the 'rockets' query with limit.
    """
    query = gql("""
        query GetRockets($limit: Int) {
            rockets(limit: $limit) {
                id
                name
                company
            }
        }
    """)
    variables = {"limit": 2}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "rockets" in result
    rockets_data = result["rockets"]
    assert isinstance(rockets_data, list)
    assert len(rockets_data) <= variables["limit"]

    for rocket in rockets_data:
        assert "id" in rocket
        assert isinstance(rocket["id"], str)
        assert "name" in rocket
        assert isinstance(rocket["name"], str)
        assert "company" in rocket
        assert isinstance(rocket["company"], str)

@pytest.mark.asyncio
async def test_rockets_result_query(graphql_client):
    """
    Tests the 'rocketsResult' query with limit.
    """
    query = gql("""
        query GetRocketsResult($limit: Int) {
            rocketsResult(limit: $limit) {
                totalCount
                rockets {
                    id
                    name
                }
            }
        }
    """)
    variables = {"limit": 2}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "rocketsResult" in result
    rockets_result = result["rocketsResult"]
    assert isinstance(rockets_result, dict)

    assert "totalCount" in rockets_result
    assert isinstance(rockets_result["totalCount"], int)

    assert "rockets" in rockets_result
    assert isinstance(rockets_result["rockets"], list)
    assert len(rockets_result["rockets"]) <= variables["limit"]

    if rockets_result["rockets"]:
        rocket = rockets_result["rockets"][0]
        assert "id" in rocket
        assert isinstance(rocket["id"], str)
        assert "name" in rocket
        assert isinstance(rocket["name"], str)

@pytest.mark.asyncio
async def test_ship_query(graphql_client):
    """
    Tests the 'ship' query with a valid ID.
    """
    query = gql("""
        query GetShip($id: ID!) {
            ship(id: $id) {
                id
                name
                type
                home_port
                legacy_id
                mass_kg
                year_built
                active
                missions {
                    name
                    flight
                }
            }
        }
    """)
    # Realistic test data: Using a known ship ID
    variables = {"id": "60264c210010000000000000"}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "ship" in result
    ship_data = result["ship"]
    assert ship_data is not None

    assert "id" in ship_data
    assert isinstance(ship_data["id"], str)
    assert ship_data["id"] == variables["id"]

    assert "name" in ship_data
    assert isinstance(ship_data["name"], str)

    assert "type" in ship_data
    assert isinstance(ship_data["type"], str)

    assert "home_port" in ship_data
    assert isinstance(ship_data["home_port"], str)

    assert "legacy_id" in ship_data
    assert isinstance(ship_data["legacy_id"], str)

    assert "mass_kg" in ship_data
    assert isinstance(ship_data["mass_kg"], int)

    assert "year_built" in ship_data
    assert isinstance(ship_data["year_built"], int)

    assert "active" in ship_data
    assert isinstance(ship_data["active"], bool)

    assert "missions" in ship_data
    assert isinstance(ship_data["missions"], list)
    if ship_data["missions"]:
        assert "name" in ship_data["missions"][0]
        assert isinstance(ship_data["missions"][0]["name"], str)
        assert "flight" in ship_data["missions"][0]
        assert isinstance(ship_data["missions"][0]["flight"], int)

@pytest.mark.asyncio
async def test_ships_query(graphql_client):
    """
    Tests the 'ships' query with limit and find.
    """
    query = gql("""
        query GetShips($limit: Int, $find: ShipsFind) {
            ships(limit: $limit, find: $find) {
                id
                name
                type
                home_port
            }
        }
    """)
    variables = {"limit": 3, "find": {"type": "Tug"}}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "ships" in result
    ships_data = result["ships"]
    assert isinstance(ships_data, list)
    assert len(ships_data) <= variables["limit"]

    for ship in ships_data:
        assert "id" in ship
        assert isinstance(ship["id"], str)
        assert "name" in ship
        assert isinstance(ship["name"], str)
        assert "type" in ship
        assert isinstance(ship["type"], str)
        assert ship["type"] == variables["find"]["type"]
        assert "home_port" in ship
        assert isinstance(ship["home_port"], str)

@pytest.mark.asyncio
async def test_ships_result_query(graphql_client):
    """
    Tests the 'shipsResult' query with limit and find.
    """
    query = gql("""
        query GetShipsResult($limit: Int, $find: ShipsFind) {
            shipsResult(limit: $limit, find: $find) {
                totalCount
                ships {
                    id
                    name
                    type
                }
            }
        }
    """)
    variables = {"limit": 2, "find": {"home_port": "Cape Canaveral"}}
    result = await graphql_client.execute(query, variable_values=variables)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "shipsResult" in result
    ships_result = result["shipsResult"]
    assert isinstance(ships_result, dict)

    assert "totalCount" in ships_result
    assert isinstance(ships_result["totalCount"], int)

    assert "ships" in ships_result
    assert isinstance(ships_result["ships"], list)
    assert len(ships_result["ships"]) <= variables["limit"]

    if ships_result["ships"]:
        ship = ships_result["ships"][0]
        assert "id" in ship
        assert isinstance(ship["id"], str)
        assert "name" in ship
        assert isinstance(ship["name"], str)
        assert "type" in ship
        assert isinstance(ship["type"], str)
        # Note: The 'find' argument for shipsResult might not directly filter the returned 'ships' list in the same way as the 'ships' query.
        # This test primarily checks the structure and presence of data.

# Note: The 'users', 'users_aggregate', and 'users_by_pk' queries are likely for internal use or a different schema.
# Without knowing the structure of 'users_select_column', 'users_order_by', and 'users_bool_exp',
# it's difficult to generate realistic test data for them.
# If these are intended for public use, more schema details would be needed.
# For now, we will skip testing these as they require specific input types not fully defined here.

@pytest.mark.asyncio
async def test__service_query(graphql_client):
    """
    Tests the '_service' query.
    """
    query = gql("""
        query {
            _service {
                sdl
            }
        }
    """)
    result = await graphql_client.execute(query)

    assert "errors" not in result, f"GraphQL errors: {result['errors']}"
    assert "_service" in result
    service_data = result["_service"]
    assert service_data is not None

    assert "sdl" in service_data
    assert isinstance(service_data["sdl"], str)
    assert len(service_data["sdl"]) > 0 # Expecting a non-empty SDL string