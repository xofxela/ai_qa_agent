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
    # Place an order first to get a valid ID
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

    response = await async_client.get(f"/store/order/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["id"] == order_id
    assert data["petId"] == order_data["petId"]

@pytest.mark.asyncio
async def test_get_order_by_invalid_id(async_client):
    """
    Tests the GET /store/order/{orderId} endpoint with an invalid (non-existent) ID.
    """
    invalid_order_id = 999999999  # Assuming this ID does not exist
    response = await async_client.get(f"/store/order/{invalid_order_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_order(async_client):
    """
    Tests the DELETE /store/order/{orderId} endpoint to delete an order.
    First, places an order to ensure an ID exists to delete.
    """
    # Place an order first to get a valid ID
    order_data = {
        "petId": 3,
        "quantity": 1,
        "shipDate": "2023-10-27T10:00:00.000Z",
        "status": "pending",
        "complete": False
    }
    place_order_response = await async_client.post("/store/order", json=order_data)
    assert place_order_response.status_code == 200
    order_id_to_delete = place_order_response.json()["id"]

    response = await async_client.delete(f"/store/order/{order_id_to_delete}")
    assert response.status_code == 200  # Successful deletion typically returns 200

    # Verify deletion by trying to get the order
    get_response = await async_client.get(f"/store/order/{order_id_to_delete}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_order(async_client):
    """
    Tests the DELETE /store/order/{orderId} endpoint with a non-existent ID.
    """
    nonexistent_order_id = 999999998  # Assuming this ID does not exist
    response = await async_client.delete(f"/store/order/{nonexistent_order_id}")
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
    # The API might return a generic success message or the created user object.
    # We'll check for a common success indicator if available, or just status code.
    # For this API, it seems to return a generic success message.

@pytest.mark.asyncio
async def test_create_users_with_list(async_client):
    """
    Tests the POST /user/createWithList endpoint to create multiple users from a list.
    """
    users_data = [
        {
            "id": 102,
            "username": "listuser1",
            "firstName": "List",
            "lastName": "One",
            "email": "listuser1@example.com",
            "password": "listpass1",
            "phone": "111-222-3333",
            "userStatus": 1
        },
        {
            "id": 103,
            "username": "listuser2",
            "firstName": "List",
            "lastName": "Two",
            "email": "listuser2@example.com",
            "password": "listpass2",
            "phone": "444-555-6666",
            "userStatus": 2
        }
    ]
    response = await async_client.post("/user/createWithList", json=users_data)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_users_with_array(async_client):
    """
    Tests the POST /user/createWithArray endpoint to create multiple users from an array.
    This is functionally similar to createWithList but uses a different endpoint.
    """
    users_data = [
        {
            "id": 104,
            "username": "arrayuser1",
            "firstName": "Array",
            "lastName": "One",
            "email": "arrayuser1@example.com",
            "password": "arraypass1",
            "phone": "777-888-9999",
            "userStatus": 1
        },
        {
            "id": 105,
            "username": "arrayuser2",
            "firstName": "Array",
            "lastName": "Two",
            "email": "arrayuser2@example.com",
            "password": "arraypass2",
            "phone": "000-111-2222",
            "userStatus": 2
        }
    ]
    response = await async_client.post("/user/createWithArray", json=users_data)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_user_by_name(async_client):
    """
    Tests the GET /user/{username} endpoint to retrieve a user by their username.
    First, creates a user to ensure it exists.
    """
    username_to_test = "testuser_get"
    user_data = {
        "id": 106,
        "username": username_to_test,
        "firstName": "Get",
        "lastName": "User",
        "email": "getuser@example.com",
        "password": "getpass",
        "phone": "123-123-1234",
        "userStatus": 1
    }
    await async_client.post("/user", json=user_data) # Create the user

    response = await async_client.get(f"/user/{username_to_test}")
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == username_to_test
    assert data["id"] == user_data["id"]

@pytest.mark.asyncio
async def test_get_nonexistent_user_by_name(async_client):
    """
    Tests the GET /user/{username} endpoint with a non-existent username.
    """
    nonexistent_username = "nonexistentuser12345"
    response = await async_client.get(f"/user/{nonexistent_username}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_user(async_client):
    """
    Tests the PUT /user/{username} endpoint to update an existing user.
    First, creates a user to ensure it exists.
    """
    original_username = "testuser_update"
    user_data = {
        "id": 107,
        "username": original_username,
        "firstName": "Update",
        "lastName": "User",
        "email": "updateuser@example.com",
        "password": "updatepass",
        "phone": "987-654-3210",
        "userStatus": 1
    }
    await async_client.post("/user", json=user_data) # Create the user

    updated_user_data = {
        "id": 107,
        "username": original_username,
        "firstName": "Updated",
        "lastName": "User",
        "email": "updateduser@example.com",
        "password": "newpassword",
        "phone": "111-111-1111",
        "userStatus": 2
    }
    response = await async_client.put(f"/user/{original_username}", json=updated_user_data)
    assert response.status_code == 200

    # Verify the update by getting the user
    get_response = await async_client.get(f"/user/{original_username}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["firstName"] == "Updated"
    assert data["email"] == "updateduser@example.com"
    assert data["userStatus"] == 2

@pytest.mark.asyncio
async def test_update_nonexistent_user(async_client):
    """
    Tests the PUT /user/{username} endpoint with a non-existent username.
    """
    nonexistent_username = "nonexistentuser_update"
    updated_user_data = {
        "id": 999,
        "username": nonexistent_username,
        "firstName": "Non",
        "lastName": "Existent",
        "email": "nonexistent@example.com",
        "password": "nopass",
        "phone": "000-000-0000",
        "userStatus": 1
    }
    response = await async_client.put(f"/user/{nonexistent_username}", json=updated_user_data)
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
        "password": "deletepass",
        "phone": "555-555-5555",
        "userStatus": 1
    }
    await async_client.post("/user", json=user_data) # Create the user

    response = await async_client.delete(f"/user/{username_to_delete}")
    assert response.status_code == 200 # Successful deletion typically returns 200

    # Verify deletion by trying to get the user
    get_response = await async_client.get(f"/user/{username_to_delete}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_user(async_client):
    """
    Tests the DELETE /user/{username} endpoint with a non-existent username.
    """
    nonexistent_username = "nonexistentuser_delete"
    response = await async_client.delete(f"/user/{nonexistent_username}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_login_user(async_client):
    """
    Tests the GET /user/login endpoint to log in a user.
    First, creates a user to ensure it exists.
    """
    username_to_login = "testuser_login"
    password_to_login = "loginpass123"
    user_data = {
        "id": 109,
        "username": username_to_login,
        "firstName": "Login",
        "lastName": "User",
        "email": "loginuser@example.com",
        "password": password_to_login,
        "phone": "123-456-7890",
        "userStatus": 1
    }
    await async_client.post("/user", json=user_data) # Create the user

    response = await async_client.get(f"/user/login?username={username_to_login}&password={password_to_login}")
    assert response.status_code == 200
    assert "logged in user session" in response.text # Or check for specific token/message

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(async_client):
    """
    Tests the GET /user/login endpoint with invalid credentials.
    """
    response = await async_client.get("/user/login?username=wronguser&password=wrongpassword")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_logout_user(async_client):
    """
    Tests the GET /user/logout endpoint to log out a user.
    Note: This endpoint might not have a visible effect without prior login state management.
    We'll test for a successful status code.
    """
    response = await async_client.get("/user/logout")
    assert response.status_code == 200
    # The response body is typically empty or a success message.