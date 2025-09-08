# credential_setup.py
"""
Helper script to set up Alpaca credentials correctly
"""

import os
import getpass

def setup_credentials():
    """Interactive credential setup"""
    print("Alpaca API Credential Setup")
    print("=" * 40)
    print("You need to get your API keys from:")
    print("https://alpaca.markets → Login → API Keys → Paper Trading")
    print()
    
    # Get paper trading credentials
    print("📋 Paper Trading Credentials:")
    paper_key_id = input("Enter your Paper Trading API Key ID: ").strip()
    paper_secret = getpass.getpass("Enter your Paper Trading Secret Key: ").strip()
    
    # Validate inputs
    if not paper_key_id or not paper_secret:
        print("❌ Error: Both API Key ID and Secret Key are required")
        return False
    
    # Validate format
    if not paper_key_id.startswith('PK'):
        print("⚠️  Warning: Paper trading keys usually start with 'PK'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Option 1: Save to environment file
    create_env = input("\nCreate .env file? (recommended) (y/n): ").strip().lower()
    if create_env == 'y':
        try:
            with open('.env', 'w') as f:
                f.write(f"ALPACA_PAPER_API_KEY={paper_key_id}\n")
                f.write(f"ALPACA_PAPER_SECRET={paper_secret}\n")
                f.write(f"# Add live trading keys when ready:\n")
                f.write(f"# ALPACA_LIVE_API_KEY=your_live_key\n")
                f.write(f"# ALPACA_LIVE_SECRET=your_live_secret\n")
            print("✅ .env file created successfully")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
    
    # Option 2: Update config file
    update_config = input("Update alpaca_config.py file? (y/n): ").strip().lower()
    if update_config == 'y':
        try:
            # Read current config
            with open('alpaca_config.py', 'r') as f:
                content = f.read()
            
            # Replace placeholder values
            content = content.replace(
                'PAPER_API_KEY_ID = os.getenv("ALPACA_PAPER_API_KEY", "YOUR_PAPER_API_KEY_ID")',
                f'PAPER_API_KEY_ID = os.getenv("ALPACA_PAPER_API_KEY", "{paper_key_id}")'
            )
            content = content.replace(
                'PAPER_SECRET_KEY = os.getenv("ALPACA_PAPER_SECRET", "YOUR_PAPER_SECRET_KEY")',
                f'PAPER_SECRET_KEY = os.getenv("ALPACA_PAPER_SECRET", "{paper_secret}")'
            )
            
            # Write updated config
            with open('alpaca_config.py', 'w') as f:
                f.write(content)
            print("✅ alpaca_config.py updated successfully")
            
        except Exception as e:
            print(f"❌ Error updating config file: {e}")
    
    # Test the credentials
    print("\n🧪 Testing credentials...")
    test_success = test_credentials(paper_key_id, paper_secret)
    
    if test_success:
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python test.py")
        print("2. Try the examples: python alpaca_examples.py")
        print("3. When ready for live trading, add live credentials")
    else:
        print("\n❌ Credential test failed. Please check your keys and try again.")
    
    return test_success

def test_credentials(api_key_id, secret_key):
    """Test credentials with direct API call"""
    import requests
    
    headers = {
        "APCA-API-KEY-ID": api_key_id,
        "APCA-API-SECRET-KEY": secret_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://paper-api.alpaca.markets/v2/account", 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connection successful!")
            print(f"   Account ID: {data.get('id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Buying Power: ${float(data.get('buying_power', 0)):,.2f}")
            return True
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def load_env_file():
    """Load environment variables from .env file"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

if __name__ == "__main__":
    # Load existing .env if it exists
    load_env_file()
    
    setup_credentials()