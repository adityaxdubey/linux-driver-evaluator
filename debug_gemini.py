import sys
sys.path.append('src')

from src.ai_integration.model_client import MultiModelClient

def debug_gemini(api_key):
    print("debugging gemini api connection")
    print("=" * 40)
    
    client = MultiModelClient("gemini", api_key)
    
    print("listing available models...")
    client.list_available_models()
    
    print("\ntesting code generation...")
    result = client.generate_driver_code("create a simple module")
    
    if result["success"]:
        print(f"success! model used: {result['model']}")
        print(f"code length: {len(result['code'])} characters")
        print("first 200 characters:")
        print(result['code'][:200] + "...")
    else:
        print(f"failed: {result['error']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python debug_gemini.py YOUR_API_KEY")
        sys.exit(1)
    
    debug_gemini(sys.argv[1])
