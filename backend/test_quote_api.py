import requests
import json

API_BASE = "http://localhost:8001/api"

def test_quote_generation():
    """Test the quote generation API endpoint"""

    # Test with a predefined theme
    test_data = {
        "theme": "motivation",
        "custom_theme": None
    }

    try:
        print("Testing quote generation API...")
        print(f"Request: {json.dumps(test_data, indent=2)}")

        response = requests.post(f"{API_BASE}/generate-quote", json=test_data, timeout=60)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("\n✅ Quote generated successfully!")
                print(f"Quote: \"{data.get('quote')}\"")
                print(f"Author: {data.get('author')}")
                print(f"Theme: {data.get('theme')}")
            else:
                print(f"\n❌ API returned success=false: {data.get('error')}")
        else:
            print(f"\n❌ API request failed with status {response.status_code}")

    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out - this is normal for AI generation")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_custom_theme():
    """Test the quote generation with custom theme"""

    test_data = {
        "theme": "",
        "custom_theme": "creativity"
    }

    try:
        print("\n" + "="*50)
        print("Testing custom theme quote generation...")
        print(f"Request: {json.dumps(test_data, indent=2)}")

        response = requests.post(f"{API_BASE}/generate-quote", json=test_data, timeout=60)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("\n✅ Custom theme quote generated successfully!")
                print(f"Quote: \"{data.get('quote')}\"")
                print(f"Author: {data.get('author')}")
                print(f"Theme: {data.get('theme')}")
            else:
                print(f"\n❌ API returned success=false: {data.get('error')}")
        else:
            print(f"\n❌ API request failed with status {response.status_code}")

    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out - this is normal for AI generation")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Test basic health check first
    try:
        health_response = requests.get(f"{API_BASE}/", timeout=10)
        print(f"Health check: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        exit(1)

    # Run quote generation tests
    test_quote_generation()
    test_custom_theme()