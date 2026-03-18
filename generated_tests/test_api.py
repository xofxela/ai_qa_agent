import pytest
import httpx

BASE_URL = "https://petstore.swagger.io/v2"

@pytest.fixture
async def async_client():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client

# --- Store Endpoints ---

@pytest.mark.asyncio
async def test_place_order(async_client):
    """
    Tests the POST /store/order endpoint to place an order for a pet.
    """
    order_data = {
        "petId": 1,
        "quantity": 1,
        "shipDate": "2023-10-27T10:00:00.000Z",
        "status": "placed",
        "complete": False
    }
    response = await async_client.post("/store/order", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["petId"] == order_data["petId"]
    assert data["quantity"] == order_data["quantity"]
    assert data["status"] == order_data["status"]

@pytest.mark.asyncio
async def test_get_order_by_id(async_client):
    """
    Tests the GET /store/order/{orderId} endpoint to retrieve an order by its ID.
    First, places an order to ensure an ID exists.
    """
    # Place an order first to get a valid order ID
    order_data = {
        "petId": 2,
        "quantity": 1,
        "shipDate": "2023-10-27T10:00:00.000Z",
        "status": "approved",
        "complete": True
    }
    place_order_response = await async_client.post("/store/order", json=order_data)
    assert place_order_response.status_code == 200
    order_id = place_order_response.json()["id"]

    # Now, get the order by ID
    response = await async_client.get(f"/store/order/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["id"] == order_id
    assert data["petId"] == order_data["petId"]

@pytest.mark.asyncio
async def test_get_order_by_invalid_id(async_client):
    """
    Tests the GET /store/order/{orderId} endpoint with an invalid ID.
    """
    response = await async_client.get("/store/order/9999999999999") # Assuming this ID does not exist
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_order(async_client):
    """
    Tests the DELETE /store/order/{orderId} endpoint to delete an order.
    First, places an order to ensure an ID exists.
    """
    # Place an order first to get a valid order ID
    order_data = {
        "petId": 3,
        "quantity": 2,
        "shipDate": "2023-10-27T11:00:00.000Z",
        "status": "pending",
        "complete": False
    }
    place_order_response = await async_client.post("/store/order", json=order_data)
    assert place_order_response.status_code == 200
    order_id = place_order_response.json()["id"]

    # Now, delete the order
    response = await async_client.delete(f"/store/order/{order_id}")
    assert response.status_code == 200 # The API returns 200 on successful deletion

    # Verify deletion by trying to get the order
    get_response = await async_client.get(f"/store/order/{order_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_order_non_existent(async_client):
    """
    Tests the DELETE /store/order/{orderId} endpoint with a non-existent ID.
    """
    response = await async_client.delete("/store/order/9999999999999") # Assuming this ID does not exist
    assert response.status_code == 404

# --- User Endpoints ---

@pytest.mark.asyncio
async def test_create_user(async_client):
    """
    Tests the POST /user endpoint to create a single user.
    """
    user_data = {
        "id": 101,
        "username": "testuser101",
        "firstName": "Test",
        "lastName": "User",
        "email": "testuser101@example.com",
        "password": "password123",
        "phone": "123-456-7890",
        "userStatus": 1
    }
    response = await async_client.post("/user", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "101" # The API returns the ID of the created user

@pytest.mark.asyncio
async def test_create_users_with_array(async_client):
    """
    Tests the POST /user/createWithArray endpoint to create multiple users.
    """
    users_data = [
        {
            "id": 102,
            "username": "testuser102",
            "firstName": "Test",
            "lastName": "User",
            "email": "testuser102@example.com",
            "password": "password123",
            "phone": "123-456-7890",
            "userStatus": 1
        },
        {
            "id": 103,
            "username": "testuser103",
            "firstName": "Another",
            "lastName": "User",
            "email": "testuser103@example.com",
            "password": "password456",
            "phone": "098-765-4321",
            "userStatus": 2
        }
    ]
    response = await async_client.post("/user/createWithArray", json=users_data)
    assert response.status_code == 200
    # The API returns a generic success message, so we check for status code.

@pytest.mark.asyncio
async def test_create_users_with_list(async_client):
    """
    Tests the POST /user/createWithList endpoint to create multiple users.
    """
    users_data = [
        {
            "id": 104,
            "username": "testuser104",
            "firstName": "List",
            "lastName": "User",
            "email": "testuser104@example.com",
            "password": "password789",
            "phone": "111-222-3333",
            "userStatus": 1
        },
        {
            "id": 105,
            "username": "testuser105",
            "firstName": "Another",
            "lastName": "List",
            "email": "testuser105@example.com",
            "password": "password000",
            "phone": "444-555-6666",
            "userStatus": 3
        }
    ]
    response = await async_client.post("/user/createWithList", json=users_data)
    assert response.status_code == 200
    # The API returns a generic success message, so we check for status code.

@pytest.mark.asyncio
async def test_get_user_by_name(async_client):
    """
    Tests the GET /user/{username} endpoint to retrieve a user by username.
    First, creates a user to ensure it exists.
    """
    username_to_test = "testuser_get"
    user_data = {
        "id": 106,
        "username": username_to_test,
        "firstName": "Get",
        "lastName": "User",
        "email": "getuser@example.com",
        "password": "getpassword",
        "phone": "555-1212",
        "userStatus": 1
    }
    await async_client.post("/user", json=user_data) # Create the user

    response = await async_client.get(f"/user/{username_to_test}")
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == username_to_test
    assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_get_user_by_non_existent_name(async_client):
    """
    Tests the GET /user/{username} endpoint with a non-existent username.
    """
    response = await async_client.get("/user/nonexistentuser12345")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user(async_client):
    """
    Tests the PUT /user/{username} endpoint to update an existing user.
    First, creates a user to ensure it exists.
    """
    username_to_update = "testuser_update"
    initial_user_data = {
        "id": 107,
        "username": username_to_update,
        "firstName": "Initial",
        "lastName": "User",
        "email": "initial@example.com",
        "password": "initialpassword",
        "phone": "111-1111",
        "userStatus": 1
    }
    await async_client.post("/user", json=initial_user_data) # Create the user

    updated_user_data = {
        "id": 107,
        "username": username_to_update,
        "firstName": "Updated",
        "lastName": "User",
        "email": "updated@example.com",
        "password": "updatedpassword",
        "phone": "222-2222",
        "userStatus": 2
    }
    response = await async_client.put(f"/user/{username_to_update}", json=updated_user_data)
    assert response.status_code == 200

    # Verify the update
    get_response = await async_client.get(f"/user/{username_to_update}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["firstName"] == "Updated"
    assert data["email"] == "updated@example.com"
    assert data["userStatus"] == 2

@pytest.mark.asyncio
async def test_update_non_existent_user(async_client):
    """
    Tests the PUT /user/{username} endpoint with a non-existent username.
    """
    response = await async_client.put("/user/nonexistentuser_update", json={
        "id": 999,
        "username": "nonexistentuser_update",
        "firstName": "Fake",
        "lastName": "User",
        "email": "fake@example.com",
        "password": "fakepassword",
        "phone": "999-9999",
        "userStatus": 1
    })
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user(async_client):
    """
    Tests the DELETE /user/{username} endpoint to delete a user.
    First, creates a user to ensure it exists.
    """
    username_to_delete = "testuser_delete"
    user_data = {
        "id": 108,
        "username": username_to_delete,
        "firstName": "Delete",
        "lastName": "User",
        "email": "deleteuser@example.com",
        "password": "deletepassword",
        "phone": "333-3333",
        "userStatus": 1
    }
    await async_client.post("/user", json=user_data) # Create the user

    response = await async_client.delete(f"/user/{username_to_delete}")
    assert response.status_code == 200 # The API returns 200 on successful deletion

    # Verify deletion by trying to get the user
    get_response = await async_client.get(f"/user/{username_to_delete}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_non_existent_user(async_client):
    """
    Tests the DELETE /user/{username} endpoint with a non-existent username.
    """
    response = await async_client.delete("/user/nonexistentuser_delete")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_login_success(async_client):
    """
    Tests the GET /user/login endpoint for a successful login.
    First, creates a user to ensure it exists.
    """
    username_to_login = "testuser_login_success"
    password_to_login = "loginpass123"
    user_data = {
        "id": 109,
        "username": username_to_login,
        "firstName": "Login",
        "lastName": "User",
        "email": "loginuser@example.com",
        "password": password_to_login,
        "phone": "444-4444",
        "userStatus": 1
    }
    await async_client.post("/user", json=user_data) # Create the user

    response = await async_client.get("/user/login", params={"username": username_to_login, "password": password_to_login})
    assert response.status_code == 200
    assert "logged in user session" in response.text # The API returns a success message string

@pytest.mark.asyncio
async def test_user_login_failure(async_client):
    """
    Tests the GET /user/login endpoint for a failed login (invalid credentials).
    """
    response = await async_client.get("/user/login", params={"username": "wronguser", "password": "wrongpassword"})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_user_logout(async_client):
    """
    Tests the GET /user/logout endpoint.
    """
    response = await async_client.get("/user/logout")
    assert response.status_code == 200
    assert "ok" in response.text.lower() # The API returns "ok" on successful logout