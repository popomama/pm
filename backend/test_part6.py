import requests
import json

print("Testing Part 6: Backend API Implementation")
print("=" * 50)

base_url = "http://localhost:8000"

print("\n1. Login to get session")
try:
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "user", "password": "password"}
    )
    assert response.status_code == 200
    session_token = response.cookies.get("session_token")
    assert session_token is not None
    print(f"   ✓ PASSED - Logged in successfully")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

cookies = {"session_token": session_token}

print("\n2. Testing GET /api/board (requires authentication)")
try:
    response = requests.get(f"{base_url}/api/board", cookies=cookies)
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200
    board = response.json()
    assert "id" in board
    assert "title" in board
    assert "columns" in board
    assert "cards" in board
    assert len(board["columns"]) == 5
    print(f"   Board ID: {board['id']}")
    print(f"   Board Title: {board['title']}")
    print(f"   Columns: {len(board['columns'])}")
    print(f"   Cards: {len(board['cards'])}")
    print(f"   ✓ PASSED - Board retrieved successfully")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    board = None

print("\n3. Testing GET /api/board without authentication")
try:
    response = requests.get(f"{base_url}/api/board")
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 401
    print(f"   ✓ PASSED - Unauthorized access blocked")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

if board:
    first_column_id = board["columns"][0]["id"]
    
    print(f"\n4. Testing POST /api/cards (create new card)")
    try:
        response = requests.post(
            f"{base_url}/api/cards",
            json={
                "columnId": first_column_id,
                "title": "Test Card",
                "details": "This is a test card"
            },
            cookies=cookies
        )
        print(f"   Status Code: {response.status_code}")
        assert response.status_code == 200
        new_card = response.json()
        assert "id" in new_card
        assert new_card["title"] == "Test Card"
        assert new_card["details"] == "This is a test card"
        assert new_card["columnId"] == first_column_id
        new_card_id = new_card["id"]
        print(f"   Created card: {new_card_id}")
        print(f"   ✓ PASSED - Card created successfully")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        new_card_id = None

    if new_card_id:
        print(f"\n5. Testing PUT /api/cards/{new_card_id} (update card)")
        try:
            response = requests.put(
                f"{base_url}/api/cards/{new_card_id}",
                json={
                    "title": "Updated Test Card",
                    "details": "Updated details"
                },
                cookies=cookies
            )
            print(f"   Status Code: {response.status_code}")
            assert response.status_code == 200
            result = response.json()
            assert result["success"] == True
            print(f"   ✓ PASSED - Card updated successfully")
        except Exception as e:
            print(f"   ✗ FAILED: {e}")

        print(f"\n6. Verify card was updated")
        try:
            response = requests.get(f"{base_url}/api/board", cookies=cookies)
            board = response.json()
            updated_card = board["cards"].get(new_card_id)
            assert updated_card is not None
            assert updated_card["title"] == "Updated Test Card"
            assert updated_card["details"] == "Updated details"
            print(f"   Card title: {updated_card['title']}")
            print(f"   ✓ PASSED - Card update verified")
        except Exception as e:
            print(f"   ✗ FAILED: {e}")

        if len(board["columns"]) > 1:
            second_column_id = board["columns"][1]["id"]
            
            print(f"\n7. Testing PUT /api/cards/{new_card_id}/move (move card)")
            try:
                response = requests.put(
                    f"{base_url}/api/cards/{new_card_id}/move",
                    json={
                        "columnId": second_column_id,
                        "position": 0
                    },
                    cookies=cookies
                )
                print(f"   Status Code: {response.status_code}")
                assert response.status_code == 200
                result = response.json()
                assert result["success"] == True
                print(f"   ✓ PASSED - Card moved successfully")
            except Exception as e:
                print(f"   ✗ FAILED: {e}")

            print(f"\n8. Verify card was moved")
            try:
                response = requests.get(f"{base_url}/api/board", cookies=cookies)
                board = response.json()
                moved_card = board["cards"].get(new_card_id)
                assert moved_card is not None
                assert moved_card["columnId"] == second_column_id
                print(f"   Card now in column: {moved_card['columnId']}")
                print(f"   ✓ PASSED - Card move verified")
            except Exception as e:
                print(f"   ✗ FAILED: {e}")

        print(f"\n9. Testing DELETE /api/cards/{new_card_id} (delete card)")
        try:
            response = requests.delete(
                f"{base_url}/api/cards/{new_card_id}",
                cookies=cookies
            )
            print(f"   Status Code: {response.status_code}")
            assert response.status_code == 200
            result = response.json()
            assert result["success"] == True
            print(f"   ✓ PASSED - Card deleted successfully")
        except Exception as e:
            print(f"   ✗ FAILED: {e}")

        print(f"\n10. Verify card was deleted")
        try:
            response = requests.get(f"{base_url}/api/board", cookies=cookies)
            board = response.json()
            assert new_card_id not in board["cards"]
            print(f"   ✓ PASSED - Card deletion verified")
        except Exception as e:
            print(f"   ✗ FAILED: {e}")

    print(f"\n11. Testing PUT /api/columns/{first_column_id} (rename column)")
    try:
        response = requests.put(
            f"{base_url}/api/columns/{first_column_id}",
            json={"title": "Test Column Name"},
            cookies=cookies
        )
        print(f"   Status Code: {response.status_code}")
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print(f"   ✓ PASSED - Column renamed successfully")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

    print(f"\n12. Verify column was renamed")
    try:
        response = requests.get(f"{base_url}/api/board", cookies=cookies)
        board = response.json()
        renamed_column = next((col for col in board["columns"] if col["id"] == first_column_id), None)
        assert renamed_column is not None
        assert renamed_column["title"] == "Test Column Name"
        print(f"   Column title: {renamed_column['title']}")
        print(f"   ✓ PASSED - Column rename verified")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

    print(f"\n13. Restore original column name")
    try:
        response = requests.put(
            f"{base_url}/api/columns/{first_column_id}",
            json={"title": "Backlog"},
            cookies=cookies
        )
        assert response.status_code == 200
        print(f"   ✓ Column name restored")
    except Exception as e:
        print(f"   Note: Could not restore column name: {e}")

print("\n" + "=" * 50)
print("Part 6 tests completed!")
print("\nAll API endpoints tested:")
print("  - GET /api/board (with authentication)")
print("  - POST /api/cards (create)")
print("  - PUT /api/cards/{id} (update)")
print("  - PUT /api/cards/{id}/move (move)")
print("  - DELETE /api/cards/{id} (delete)")
print("  - PUT /api/columns/{id} (rename)")
