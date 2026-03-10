"""Test script for Microsoft Foundry Agent"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_agent():
    """Test the Azure agent with a simple question"""
    print("=" * 60)
    print("🧪 Testing Microsoft Foundry Agent")
    print("=" * 60)
    print()
    
    try:
        from app.azure_agent import ask_agent
        
        # Test questions
        test_questions = [
            "Hi Agent165",
            "What can you help me with?",
            "Tell me about yourself"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Test {i}/{len(test_questions)}")
            print(f"Question: {question}")
            print("-" * 60)
            
            try:
                response = ask_agent(question)
                print(f"Response: {response}")
                print("✅ Success!")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
            print("-" * 60)
        
        print("\n" + "=" * 60)
        print("✅ Agent testing complete!")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease make sure you have installed the dependencies:")
        print("  pip install -r app/requirements.txt")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease check:")
        print("  1. .env file exists with correct values")
        print("  2. Azure authentication (run: az login)")
        print("  3. Agent ID and connection string are correct")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()

