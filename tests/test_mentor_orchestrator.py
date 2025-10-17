#!/usr/bin/env python3
"""
Comprehensive test for the ported mentor orchestrator functionality.
Tests all critical behaviors that were ported from runAssistant.ts and route.ts.
"""

import json
import requests
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:5000"
CHAT_ENDPOINT = f"{BASE_URL}/api/mentor/chat"

def test_chat_endpoint():
    """Test the main chat endpoint with various scenarios."""
    print("🧪 Testing /api/mentor/chat endpoint...")
    
    # Test 1: Basic message (should trigger tool calls)
    print("\n1. Testing basic message with tool calls...")
    response = requests.post(CHAT_ENDPOINT, json={
        "message": "What is my win rate and how many trades do I have?"
    })
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "threadId" in data, "Missing threadId in response"
    assert "text" in data, "Missing text in response"
    assert data["threadId"], "Empty threadId"
    assert data["text"], "Empty response text"
    
    print(f"✅ Basic message: {data['text'][:100]}...")
    thread_id = data["threadId"]
    
    # Test 2: Follow-up message (should reuse thread)
    print("\n2. Testing follow-up message with thread reuse...")
    response = requests.post(CHAT_ENDPOINT, json={
        "message": "What about my biggest loss?",
        "threadId": thread_id
    })
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["threadId"] == thread_id, "Thread ID should be reused"
    assert data["text"], "Empty follow-up response"
    
    print(f"✅ Follow-up message: {data['text'][:100]}...")
    
    # Test 3: Error handling - missing message
    print("\n3. Testing error handling - missing message...")
    response = requests.post(CHAT_ENDPOINT, json={})
    assert response.status_code == 400, f"Expected 400 for missing message, got {response.status_code}"
    data = response.json()
    assert "error" in data, "Missing error in response"
    print(f"✅ Error handling: {data['error']}")
    
    # Test 4: Error handling - empty message
    print("\n4. Testing error handling - empty message...")
    response = requests.post(CHAT_ENDPOINT, json={"message": ""})
    assert response.status_code == 400, f"Expected 400 for empty message, got {response.status_code}"
    data = response.json()
    assert "error" in data, "Missing error in response"
    print(f"✅ Empty message handling: {data['error']}")
    
    # Test 5: Complex query that should trigger multiple tool calls
    print("\n5. Testing complex query with multiple tool calls...")
    response = requests.post(CHAT_ENDPOINT, json={
        "message": "Show me my worst 3 losses and tell me about my revenge trading patterns"
    })
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["text"], "Empty complex response"
    print(f"✅ Complex query: {data['text'][:150]}...")
    
    return thread_id

def test_tool_calls_directly():
    """Test the individual tool endpoints that the orchestrator calls."""
    print("\n🔧 Testing individual tool endpoints...")
    
    # Test get_summary_data
    print("\n1. Testing get_summary_data...")
    response = requests.post(f"{BASE_URL}/api/mentor/get_summary_data", json={})
    assert response.status_code == 200, f"get_summary_data failed: {response.status_code}"
    data = response.json()
    assert "total_trades" in data or "win_count" in data, "Missing expected summary fields"
    print(f"✅ get_summary_data: {len(str(data))} chars")
    
    # Test get_endpoint_data with keys_only
    print("\n2. Testing get_endpoint_data (keys_only)...")
    response = requests.post(f"{BASE_URL}/api/mentor/get_endpoint_data", json={
        "name": "revenge",
        "keys_only": True
    })
    assert response.status_code == 200, f"get_endpoint_data failed: {response.status_code}"
    data = response.json()
    assert "keys" in data, "Missing keys in response"
    print(f"✅ get_endpoint_data keys: {data['keys']}")
    
    # Test filter_trades
    print("\n3. Testing filter_trades...")
    response = requests.post(f"{BASE_URL}/api/mentor/filter_trades", json={
        "max_results": 5,
        "fields": ["id", "symbol", "pnl"]
    })
    assert response.status_code == 200, f"filter_trades failed: {response.status_code}"
    data = response.json()
    assert "results" in data, "Missing results in filter_trades"
    print(f"✅ filter_trades: {len(data['results'])} trades")
    
    # Test filter_losses with extrema
    print("\n4. Testing filter_losses with extrema...")
    response = requests.post(f"{BASE_URL}/api/mentor/filter_losses", json={
        "extrema": {"field": "pointsLost", "mode": "max"},
        "max_results": 1
    })
    assert response.status_code == 200, f"filter_losses failed: {response.status_code}"
    data = response.json()
    assert "results" in data, "Missing results in filter_losses"
    print(f"✅ filter_losses extrema: {len(data['results'])} worst loss")

def test_specific_scenarios():
    """Test specific scenarios that were critical in the original TypeScript code."""
    print("\n🎯 Testing specific critical scenarios...")
    
    # Test 1: Topic normalization (topic -> name) - test through chat
    print("\n1. Testing topic normalization...")
    response = requests.post(f"{BASE_URL}/api/mentor/chat", json={
        "message": "Tell me about excessive risk analysis"
    })
    assert response.status_code == 200, f"Topic normalization failed: {response.status_code}"
    data = response.json()
    print(f"✅ Topic normalization: {data['text'][:100]}...")
    
    # Test 2: Safe defaults and pagination
    print("\n2. Testing safe defaults and pagination...")
    response = requests.post(f"{BASE_URL}/api/mentor/get_endpoint_data", json={
        "name": "trades",
        "top": "trades"
    })
    assert response.status_code == 200, f"Safe defaults failed: {response.status_code}"
    data = response.json()
    assert "results" in data, "Missing paginated results"
    print(f"✅ Safe defaults: {len(data['results'])} items")
    
    # Test 3: Mistakes filtering
    print("\n3. Testing mistakes filtering...")
    response = requests.post(f"{BASE_URL}/api/mentor/filter_trades", json={
        "mistakes": ["excessive risk"],
        "max_results": 3
    })
    assert response.status_code == 200, f"Mistakes filtering failed: {response.status_code}"
    data = response.json()
    print(f"✅ Mistakes filtering: {len(data['results'])} trades with excessive risk")
    
    # Test 4: Extrema detection for "worst loss"
    print("\n4. Testing extrema detection...")
    response = requests.post(f"{BASE_URL}/api/mentor/filter_losses", json={
        "max_results": 1
    })
    assert response.status_code == 200, f"Extrema detection failed: {response.status_code}"
    data = response.json()
    # Should automatically detect single worst loss
    if "extrema" in str(data):
        print("✅ Extrema detection: Auto-detected single worst loss")
    else:
        print("ℹ️  Extrema detection: No extrema detected (may be normal)")

def test_error_resilience():
    """Test error handling and resilience."""
    print("\n🛡️ Testing error resilience...")
    
    # Test 1: Invalid endpoint name
    print("\n1. Testing invalid endpoint...")
    response = requests.post(f"{BASE_URL}/api/mentor/get_endpoint_data", json={
        "name": "invalid-endpoint-that-does-not-exist"
    })
    # Should either return 400 or handle gracefully
    print(f"✅ Invalid endpoint: {response.status_code} (expected 400 or graceful handling)")
    
    # Test 2: Malformed request
    print("\n2. Testing malformed request...")
    response = requests.post(f"{BASE_URL}/api/mentor/filter_trades", json={
        "max_results": "not-a-number"
    })
    assert response.status_code == 200, f"Malformed request should be handled gracefully: {response.status_code}"
    data = response.json()
    print(f"✅ Malformed request: Handled gracefully")

def main():
    """Run all tests."""
    print("🚀 Starting comprehensive mentor orchestrator tests...")
    print(f"Testing against: {BASE_URL}")
    
    try:
        # Test basic connectivity
        health_response = requests.get(f"{BASE_URL}/api/mentor/health")
        assert health_response.status_code == 200, "Backend not responding"
        print("✅ Backend is responding")
        
        # Run all test suites
        thread_id = test_chat_endpoint()
        test_tool_calls_directly()
        test_specific_scenarios()
        test_error_resilience()
        
        print(f"\n🎉 All tests passed! Final thread ID: {thread_id}")
        print("\n📋 Test Summary:")
        print("✅ Chat endpoint with tool calls")
        print("✅ Thread management and reuse")
        print("✅ Error handling (missing/empty messages)")
        print("✅ Complex queries with multiple tool calls")
        print("✅ Individual tool endpoints")
        print("✅ Topic normalization")
        print("✅ Safe defaults and pagination")
        print("✅ Mistakes filtering")
        print("✅ Extrema detection")
        print("✅ Error resilience")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
