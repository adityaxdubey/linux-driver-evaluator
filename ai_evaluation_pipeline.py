# ai_evaluation_pipeline.py
import sys
import json
import argparse
from datetime import datetime

sys.path.append('src')
from src.ai_integration.model_client import AIModelClient, MockAIClient
from src.evaluator.main_evaluator import DriverModelEvaluator
from tests.test_cases.sample_prompts import SAMPLE_PROMPTS

class AIEvaluationPipeline:
    def __init__(self, use_mock: bool = True, api_key: str = None):
        if use_mock or not api_key:
            self.ai_client = MockAIClient("mock-gpt")
            print("Using mock AI client for testing")
        else:
            self.ai_client = AIModelClient(api_key, "gpt-3.5-turbo")
            print("Using OpenAI GPT client")
        
        self.evaluator = DriverModelEvaluator()
    
    def run_single_evaluation(self, prompt: str, prompt_id: str = None):
        """Run evaluation on a single prompt"""
        print(f"Generating code for prompt: {prompt[:50]}...")
        
        # Generate code using AI
        generation_result = self.ai_client.generate_driver_code(prompt)
        
        if not generation_result["success"]:
            print(f"Error generating code: {generation_result['error']}")
            return None
        
        code = generation_result["code"]
        model_name = generation_result["model"]
        
        print(f"Generated {len(code)} characters of code")
        
        # Evaluate the generated code
        prompt_info = {"id": prompt_id or "custom", "prompt": prompt}
        evaluation_result = self.evaluator.evaluate_single_code(code, prompt_info, model_name)
        
        # Add generation info to result
        evaluation_result["generation_info"] = {
            "tokens_used": generation_result.get("tokens_used", 0),
            "generation_success": True
        }
        
        return evaluation_result
    
    def run_benchmark_suite(self):
        """Run evaluation on all sample prompts"""
        print("Running AI Model Benchmark Suite")
        print("=" * 50)
        
        results = []
        
        for i, prompt_data in enumerate(SAMPLE_PROMPTS):
            print(f"\n[{i+1}/{len(SAMPLE_PROMPTS)}] Processing: {prompt_data['id']}")
            
            result = self.run_single_evaluation(prompt_data["prompt"], prompt_data["id"])
            
            if result:
                results.append(result)
                score = result["scores"]["overall_score"]
                print(f"Score: {score:.1f}/100")
            else:
                print("Failed to generate/evaluate code")
        
        # Generate benchmark report
        if results:
            self._generate_benchmark_report(results)
        
        return results
    
    def run_custom_prompts(self, prompts: list):
        """Run evaluation on custom prompts"""
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"\n[{i+1}/{len(prompts)}] Custom prompt evaluation")
            result = self.run_single_evaluation(prompt, f"custom_{i+1}")
            
            if result:
                results.append(result)
                score = result["scores"]["overall_score"]
                print(f"Score: {score:.1f}/100")
        
        return results
    
    def _generate_benchmark_report(self, results: list):
        """Generate simple benchmark report"""
        scores = [r["scores"]["overall_score"] for r in results]
        
        report = {
            "benchmark_summary": {
                "total_tests": len(results),
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "timestamp": datetime.now().isoformat()
            },
            "score_distribution": {
                "excellent_90_plus": len([s for s in scores if s >= 90]),
                "good_70_89": len([s for s in scores if 70 <= s < 90]),
                "fair_50_69": len([s for s in scores if 50 <= s < 70]),
                "poor_below_50": len([s for s in scores if s < 50])
            },
            "detailed_results": results
        }
        
        # Save report
        filename = f"results/ai_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nBenchmark Report:")
        print(f"Average Score: {report['benchmark_summary']['average_score']:.1f}/100")
        print(f"Score Range: {report['benchmark_summary']['min_score']:.1f} - {report['benchmark_summary']['max_score']:.1f}")
        print(f"Report saved: {filename}")

def main():
    parser = argparse.ArgumentParser(description='AI Model Evaluation Pipeline')
    parser.add_argument('--benchmark', '-b', action='store_true', 
                       help='Run full benchmark suite')
    parser.add_argument('--prompt', '-p', type=str, 
                       help='Single prompt to evaluate')
    parser.add_argument('--api-key', type=str, 
                       help='OpenAI API key (uses mock if not provided)')
    parser.add_argument('--custom-prompts', nargs='+', 
                       help='Multiple custom prompts')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = AIEvaluationPipeline(
        use_mock=(args.api_key is None), 
        api_key=args.api_key
    )
    
    if args.benchmark:
        pipeline.run_benchmark_suite()
    elif args.prompt:
        result = pipeline.run_single_evaluation(args.prompt)
        if result:
            score = result["scores"]["overall_score"]
            print(f"\nFinal Score: {score:.1f}/100")
    elif args.custom_prompts:
        pipeline.run_custom_prompts(args.custom_prompts)
    else:
        print("AI Model Evaluation Pipeline")
        print("Usage examples:")
        print("  python ai_evaluation_pipeline.py --benchmark")
        print("  python ai_evaluation_pipeline.py --prompt 'Create a simple character driver'")
        print("  python ai_evaluation_pipeline.py --custom-prompts 'prompt1' 'prompt2'")
        print("\nNote: Using mock AI client. Add --api-key for real OpenAI integration")

if __name__ == "__main__":
    main()
