# config.py
import os

class Config:
    # API Settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
    DEFAULT_MODEL = "gpt-3.5-turbo"
    
    # Evaluation Settings
    RESULTS_DIR = "results"
    MAX_TOKENS = 1500
    TEMPERATURE = 0.1
    
    # Scoring Weights
    SCORING_WEIGHTS = {
        "compilation": 0.4,
        "functionality": 0.25,
        "security": 0.20,
        "code_quality": 0.10,
        "advanced_features": 0.05
    }
    
    # Analysis Settings
    MAX_LINE_LENGTH = 100
    MAX_VIOLATIONS_SHOWN = 5
    MAX_RECOMMENDATIONS = 8
