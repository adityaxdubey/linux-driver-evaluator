import json
from datetime import datetime
from typing import Dict, Any

class DriverEvaluationMetrics:
    def __init__(self):
        self.metrics = {
            "compilation": {
                "success_rate": 0.0,
                "warnings_count": 0,
                "errors_count": 0,
                "weight": 0.4
            },
            "functionality": {
                "basic_operations": 0.0,
                "error_handling": 0.0,
                "kernel_api_usage": 0.0,
                "weight": 0.25
            },
            "security": {
                "buffer_safety": 0.0,
                "memory_management": 0.0,
                "input_validation": 0.0,
                "weight": 0.20
            },
            "code_quality": {
                "style_compliance": 0.0,
                "documentation": 0.0,
                "maintainability": 0.0,
                "weight": 0.10
            },
            "advanced_features": {
                "error_recovery": 0.0,
                "resource_cleanup": 0.0,
                "weight": 0.05
            }
        }
        self.timestamp = datetime.now().isoformat()
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        total_score = 0.0
        
        for category, data in self.metrics.items():
            if isinstance(data, dict) and 'weight' in data:
                # Calculate average score for this category
                scores = [v for k, v in data.items() if k != 'weight' and isinstance(v, (int, float))]
                if scores:
                    category_avg = sum(scores) / len(scores)
                    total_score += category_avg * data['weight']
        
        return min(100.0, total_score * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format"""
        return {
            "metrics": self.metrics,
            "overall_score": self.calculate_overall_score(),
            "timestamp": self.timestamp
        }
    
    def save_to_file(self, filepath: str):
        """Save metrics to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
