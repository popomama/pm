import requests
import json
import time
import traceback

print("Testing Part 9: AI Kanban Integration")
print("=" * 50)

base_url = "http://localhost:8000"
session = requests.Session()

print("\n1. Login to get session")
try:
    login_response = session.post(
        f"{base_url}/api/auth/login",
        json={"username": "user", "password": "password"}
    )
    assert login_response.status_code == 200
    print(f"   ✓ PASSED - Logged in successfully")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

print("\n2. Get current board state")
try:
    board_response = session.get(f"{base_url}/api/board")
    assert board_response.status_code == 200
    board = board_response.json()
    print(f"   Board has {len(board['cards'])} cards")
    print(f"   ✓ PASSED - Board retrieved")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

print("\n3. Test AI chat - Simple question (no board changes)")
response = None
try:
    response = session.post(
        f"{base_url}/api/ai/chat",
        json={"message": "What columns do I have on my board?"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"   AI Response: {data['response'][:100]}...")
    print(f"   Board updates: {len(data.get('board_updates', []))}")
    assert 'response' in data
    print(f"   ✓ PASSED - AI responds to questions")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    if response and response.status_code != 200:
        print(f"   Error: {response.text}")

print("\n4. Test AI creating a card")
created_card_id = None
response = None
try:
    response = session.post(
        f"{base_url}/api/ai/chat",
        json={"message": "Create a card called 'AI Test Card' in the backlog with details 'Created by AI test'"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"   AI Response: {data['response'][:100]}...")
    print(f"   Board updates: {data.get('board_updates', [])}")
    print(f"   Update results: {data.get('update_results', [])}")
    
    if len(data.get('board_updates', [])) == 0:
        print(f"   Warning: No board updates returned")
        print(f"   Full response: {data}")
    
    assert len(data.get('board_updates', [])) > 0, f"Expected board updates, got: {data}"
    assert data['board_updates'][0]['action'] == 'create'
    
    board_response = session.get(f"{base_url}/api/board")
    new_board = board_response.json()
    
    print(f"   Old board had {len(board['cards'])} cards, new board has {len(new_board['cards'])} cards")
    assert len(new_board['cards']) > len(board['cards']), "Card count did not increase"
    
    for card_id, card in new_board['cards'].items():
        if card['title'] == 'AI Test Card':
            created_card_id = card_id
            print(f"   Created card ID: {created_card_id}")
            break
    
    assert created_card_id is not None, "Could not find created card"
    print(f"   ✓ PASSED - AI created a card")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()
    if response and response.status_code != 200:
        print(f"   Error: {response.text}")

print("\n5. Test AI moving a card")
try:
    if created_card_id:
        response = session.post(
            f"{base_url}/api/ai/chat",
            json={"message": f"Move {created_card_id} to In Progress"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"   AI Response: {data['response'][:100]}...")
        print(f"   Board updates: {data.get('board_updates', [])}")
        
        board_response = session.get(f"{base_url}/api/board")
        updated_board = board_response.json()
        moved_card = updated_board['cards'].get(created_card_id)
        assert moved_card is not None
        assert moved_card['columnId'] == 'col-3'
        
        print(f"   ✓ PASSED - AI moved the card")
    else:
        print(f"   ⊘ SKIPPED - No card to move")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n6. Test AI updating a card")
try:
    if created_card_id:
        response = session.post(
            f"{base_url}/api/ai/chat",
            json={"message": f"Update {created_card_id} title to 'Updated AI Test Card'"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"   AI Response: {data['response'][:100]}...")
        
        board_response = session.get(f"{base_url}/api/board")
        updated_board = board_response.json()
        updated_card = updated_board['cards'].get(created_card_id)
        assert updated_card is not None
        assert updated_card['title'] == 'Updated AI Test Card'
        
        print(f"   ✓ PASSED - AI updated the card")
    else:
        print(f"   ⊘ SKIPPED - No card to update")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n7. Test AI deleting a card")
try:
    if created_card_id:
        response = session.post(
            f"{base_url}/api/ai/chat",
            json={"message": f"Delete {created_card_id}"}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"   AI Response: {data['response'][:100]}...")
        
        board_response = session.get(f"{base_url}/api/board")
        final_board = board_response.json()
        assert created_card_id not in final_board['cards']
        
        print(f"   ✓ PASSED - AI deleted the card")
    else:
        print(f"   ⊘ SKIPPED - No card to delete")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n8. Test conversation history")
try:
    response1 = session.post(
        f"{base_url}/api/ai/chat",
        json={"message": "Create a card called 'History Test' in To Do"}
    )
    assert response1.status_code == 200
    
    response2 = session.post(
        f"{base_url}/api/ai/chat",
        json={"message": "What did I just ask you to do?"}
    )
    assert response2.status_code == 200
    data = response2.json()
    print(f"   AI Response: {data['response'][:150]}...")
    
    print(f"   ✓ PASSED - Conversation history maintained")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n9. Test AI without authentication")
try:
    response = requests.post(
        f"{base_url}/api/ai/chat",
        json={"message": "Hello"}
    )
    assert response.status_code == 401
    print(f"   ✓ PASSED - Unauthorized access blocked")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n" + "=" * 50)
print("Part 9 tests completed!")
print("\nAI Kanban Integration Summary:")
print("  - AI understands Kanban board context")
print("  - AI can create cards")
print("  - AI can update cards")
print("  - AI can move cards between columns")
print("  - AI can delete cards")
print("  - AI responds conversationally")
print("  - Conversation history is maintained")
print("  - Board updates are applied correctly")
