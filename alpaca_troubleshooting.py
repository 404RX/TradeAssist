# alpaca_troubleshooting.py
"""
Troubleshooting script for Alpaca API connection issues
"""

import os
import requests
import base64

def check_credentials():
    """Check if credentials are properly configured"""
    print("=== Credential Check ===")
    
    # Check environment variables first
    paper_key = os.getenv("ALPACA_PAPER_API_KEY")
    paper_secret = os.getenv("ALPACA_PAPER_SECRET")
    
    print(f"Environment variable ALPACA_PAPER_API_KEY: {'✓ Set' if paper_key else '✗ Not set'}")
    print(f"Environment variable ALPACA_PAPER_SECRET: {'✓ Set' if paper_secret else '✗ Not set'}")
    
    if paper_key:
        print(f"Paper API Key (first 8 chars): {paper_key[:8]}...")
    if paper_secret:
        print(f"Paper Secret (first 8 chars): {paper_secret[:8]}...")
    
    # Check config file
    try:
        from alpaca_config import PAPER_API_KEY_ID, PAPER_SECRET_KEY
        
        config_key_valid = PAPER_API_KEY_ID not in ["", "YOUR_PAPER_API_KEY_ID"]
        config_secret_valid = PAPER_SECRET_KEY not in ["", "YOUR_PAPER_SECRET_KEY"]
        
        print(f"Config file PAPER_API_KEY_ID: {'✓ Set' if config_key_valid else '✗ Default placeholder'}")
        print(f"Config file PAPER_SECRET_KEY: {'✓ Set' if config_secret_valid else '✗ Default placeholder'}")
        
        if config_key_valid:
            print(f"Config API Key (first 8 chars): {PAPER_API_KEY_ID[:8]}...")
        if config_secret_valid:
            print(f"Config Secret (first 8 chars): {PAPER_SECRET_KEY[:8]}...")
            
        return config_key_valid and config_secret_valid
        
    except ImportError as e:
        print(f"✗ Cannot import config: {e}")
        return False

def test_direct_api_call(api_key_id, secret_key):
    """Test direct API call to Alpaca"""
    print(f"\n=== Direct API Test ===")
    print(f"Testing with Key ID: {api_key_id[:8]}...")
    
    headers = {
        "APCA-API-KEY-ID": api_key_id,
        "APCA-API-SECRET-KEY": secret_key,
        "Content-Type": "application/json"
    }
    
    # Test paper trading endpoint
    url = "https://paper-api.alpaca.markets/v2/account"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ API connection successful!")
            print(f"Account ID: {data.get('id', 'Unknown')}")
            print(f"Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"✗ API Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False

def validate_key_format(api_key_id, secret_key):
    """Validate API key format"""
    print(f"\n=== Key Format Validation ===")
    
    # Alpaca paper trading keys typically start with "PK" for key ID
    key_id_valid = len(api_key_id) > 10 and api_key_id.startswith(('PK', 'AK'))
    secret_valid = len(secret_key) > 20
    
    print(f"Key ID format: {'✓ Valid' if key_id_valid else '✗ Invalid'}")
    print(f"Key ID length: {len(api_key_id)} chars")
    print(f"Key ID starts with: {api_key_id[:2]}...")
    
    print(f"Secret format: {'✓ Valid' if secret_valid else '✗ Invalid'}")
    print(f"Secret length: {len(secret_key)} chars")
    
    return key_id_valid and secret_valid

def check_network_connectivity():
    """Check network connectivity to Alpaca"""
    print(f"\n=== Network Connectivity ===")
    
    urls_to_test = [
        "https://paper-api.alpaca.markets",
        "https://api.alpaca.markets",
        "https://data.alpaca.markets"
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=5)
            print(f"✓ {url} - Reachable (Status: {response.status_code})")
        except requests.RequestException as e:
            print(f"✗ {url} - Unreachable: {e}")

def main():
    """Main troubleshooting function"""
    print("Alpaca API Troubleshooting")
    print("=" * 50)
    
    # Step 1: Check credentials
    if not check_credentials():
        print("\n❌ ISSUE: Credentials not properly configured")
        print("\nSOLUTIONS:")
        print("1. Set environment variables:")
        print("   export ALPACA_PAPER_API_KEY='your_key_here'")
        print("   export ALPACA_PAPER_SECRET='your_secret_here'")
        print("\n2. Or edit alpaca_config.py with your actual keys")
        print("\n3. Get keys from: https://alpaca.markets → API Keys → Paper Trading")
        return
    
    # Step 2: Get credentials for testing
    try:
        from alpaca_config import PAPER_API_KEY_ID, PAPER_SECRET_KEY
        
        # Use environment variables if available, otherwise config file
        api_key_id = os.getenv("ALPACA_PAPER_API_KEY", PAPER_API_KEY_ID)
        secret_key = os.getenv("ALPACA_PAPER_SECRET", PAPER_SECRET_KEY)
        
    except ImportError:
        print("❌ Cannot import configuration")
        return
    
    # Step 3: Validate key format
    if not validate_key_format(api_key_id, secret_key):
        print("\n❌ ISSUE: Invalid key format")
        print("\nSOLUTIONS:")
        print("1. Verify you copied the keys correctly")
        print("2. Paper trading Key ID should start with 'PK'")
        print("3. Live trading Key ID should start with 'AK'")
        print("4. Regenerate keys if necessary")
        return
    
    # Step 4: Check network connectivity
    check_network_connectivity()
    
    # Step 5: Test direct API call
    if test_direct_api_call(api_key_id, secret_key):
        print("\n✅ SUCCESS: API connection working!")
        print("\nYour credentials are correct. The issue might be in your client code.")
        
        # Test with the actual client
        print("\n=== Testing with AlpacaTradingClient ===")
        try:
            from alpaca_config import get_client, TradingMode
            client = get_client(TradingMode.PAPER)
            account = client.get_account()
            print("✅ AlpacaTradingClient working correctly!")
            print(f"Account Status: {account['status']}")
            print(f"Buying Power: ${float(account['buying_power']):,.2f}")
        except Exception as e:
            print(f"✗ AlpacaTradingClient failed: {e}")
    else:
        print("\n❌ ISSUE: API connection failed")
        print("\nCOMMON SOLUTIONS:")
        print("1. Double-check your API keys in Alpaca dashboard")
        print("2. Ensure you're using PAPER TRADING keys")
        print("3. Regenerate your API keys")
        print("4. Check if your account is active")
        print("5. Verify no IP restrictions on your keys")

if __name__ == "__main__":
    main()