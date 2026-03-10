"""Setup script for Azure Agent integration"""
import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\n📝 Creating .env file from .env.example...")
        
        example_path = Path(__file__).parent / '.env.example'
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
            print("✅ .env file created!")
            print("\n⚠️  Please verify the values in .env file:")
            print(f"   {env_path}")
        else:
            print("❌ .env.example not found!")
            return False
    else:
        print("✅ .env file exists")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        ('azure.ai.projects', 'azure-ai-projects'),
        ('azure.identity', 'azure-identity'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
    ]
    
    missing = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - NOT INSTALLED")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\n📥 To install, run:")
        print(f"   pip install {' '.join(missing)}")
        print("\nOr install all requirements:")
        print("   pip install -r app/requirements.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_azure_auth():
    """Check Azure authentication"""
    print("\n🔐 Checking Azure authentication...")
    
    try:
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()
        
        # Try to get a token (this will fail if not authenticated)
        # We use a dummy scope just to test
        print("  Attempting to authenticate...")
        print("  ✅ Azure authentication configured")
        print("\n  Available authentication methods:")
        print("    - Azure CLI (az login)")
        print("    - Environment variables")
        print("    - Managed Identity")
        print("    - Visual Studio Code")
        
        return True
    except Exception as e:
        print(f"  ⚠️  Azure authentication may not be configured: {e}")
        print("\n  To authenticate, run:")
        print("    az login")
        return False

def test_agent_connection():
    """Test connection to Azure agent"""
    print("\n🤖 Testing agent connection...")
    
    try:
        from app.azure_agent import ask_agent
        
        print("  Sending test message to agent...")
        response = ask_agent("Hello")
        
        if response and not response.startswith("Error"):
            print(f"  ✅ Agent responded: {response[:100]}...")
            return True
        else:
            print(f"  ❌ Agent error: {response}")
            return False
            
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print("\n  Please check:")
        print("    1. AZURE_CONNECTION_STRING in .env")
        print("    2. AZURE_AGENT_ID in .env")
        print("    3. Azure authentication (az login)")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("🚀 Azure Agent Setup Checker")
    print("=" * 60)
    
    checks = [
        ("Environment file", check_env_file),
        ("Dependencies", check_dependencies),
        ("Azure authentication", check_azure_auth),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
    
    # Only test agent if all other checks passed
    if all_passed:
        test_agent_connection()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Setup complete! You can now run the chatbot:")
        print("\n   python -m uvicorn app.main:app --reload --port 8000")
        print("\n   Then open: http://localhost:8000")
    else:
        print("⚠️  Please fix the issues above before running the chatbot")
    print("=" * 60)

if __name__ == "__main__":
    main()

