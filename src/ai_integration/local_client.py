import requests
import json

class LocalAIClient:
    """Client for local AI models like Ollama"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "codellama"
    
    def generate_driver_code(self, prompt: str, max_tokens: int = 1500) -> dict:
        try:
            response = requests.post(f"{self.base_url}/api/generate", 
                                   json={
                                       "model": self.model_name,
                                       "prompt": f"Create Linux kernel driver code: {prompt}",
                                       "stream": False
                                   })
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "code": result.get("response", ""),
                    "model": self.model_name,
                    "tokens_used": 500
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
