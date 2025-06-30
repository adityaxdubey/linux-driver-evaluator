import sys
import json
import argparse
from datetime import datetime

sys.path.append('src')
from src.ai_integration.model_client import MultiModelClient
from src.evaluator.enhanced_evaluator import EnhancedDriverEvaluator
from tests.test_cases.sample_prompts import SAMPLE_PROMPTS

class AIEvaluationPipeline:
    def __init__(self, model_type: str = "mock", api_key: str = None):
        self.ai_client = MultiModelClient(model_type, api_key)
        self.evaluator = EnhancedDriverEvaluator()
        self.model_type = model_type
    
    def run_single_evaluation(self, prompt: str, prompt_id: str = None):
        """run evaluation on a single prompt"""
        print(f"generating code using {self.model_type} model...")
        print(f"prompt: {prompt[:50]}...")
        
        # generate code using ai
        generation_result = self.ai_client.generate_driver_code(prompt)
        
        if not generation_result["success"]:
            print(f"error generating code: {generation_result['error']}")
            return None
        
        code = generation_result["code"]
        model_name = generation_result["model"]
        
        print(f"generated {len(code)} characters of code")
        
        # evaluate the generated code
        prompt_info = {"id": prompt_id or "custom", "prompt": prompt}
        evaluation_result = self.evaluator.comprehensive_evaluation(code, prompt_info)
        
        # add generation info
        evaluation_result["generation_info"] = {
            "model_used": model_name,
            "tokens_used": generation_result.get("tokens_used", 0),
            "generation_success": True
        }
        
        return evaluation_result
    
    def run_benchmark_suite(self):
        """run evaluation on all sample prompts"""
        print(f"running ai model benchmark suite with {self.model_type}")
        print("=" * 60)
        
        results = []
        
        for i, prompt_data in enumerate(SAMPLE_PROMPTS):
            print(f"\n[{i+1}/{len(SAMPLE_PROMPTS)}] processing: {prompt_data['id']}")
            
            result = self.run_single_evaluation(prompt_data["prompt"], prompt_data["id"])
            
            if result:
                results.append(result)
                score = result["enhanced_score"]
                clang_score = result.get('clang_analysis', {}).get('summary', {}).get('clang_score', 0)
                print(f"enhanced score: {score:.1f}/100")
                print(f"clang score: {clang_score:.1f}/100")
            else:
                print("failed to generate/evaluate code")
        
        # generate benchmark report
        if results:
            self._generate_benchmark_report(results)
        
        return results
    
    def run_custom_prompts(self, prompts: list):
        """run evaluation on custom prompts"""
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"\n[{i+1}/{len(prompts)}] custom prompt evaluation")
            result = self.run_single_evaluation(prompt, f"custom_{i+1}")
            
            if result:
                results.append(result)
                score = result["enhanced_score"]
                print(f"enhanced score: {score:.1f}/100")
        
        return results
    
    def _generate_benchmark_report(self, results: list):
        """generate benchmark report"""
        enhanced_scores = [r["enhanced_score"] for r in results]
        clang_scores = [r.get('clang_analysis', {}).get('summary', {}).get('clang_score', 0) for r in results]
        
        report = {
            "benchmark_summary": {
                "model_type": self.model_type,
                "total_tests": len(results),
                "average_enhanced_score": sum(enhanced_scores) / len(enhanced_scores),
                "average_clang_score": sum(clang_scores) / len(clang_scores),
                "min_enhanced_score": min(enhanced_scores),
                "max_enhanced_score": max(enhanced_scores),
                "timestamp": datetime.now().isoformat()
            },
            "detailed_results": results
        }
        
        # save report
        filename = f"results/ai_benchmark_{self.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nbenchmark report:")
        print(f"average enhanced score: {report['benchmark_summary']['average_enhanced_score']:.1f}/100")
        print(f"average clang score: {report['benchmark_summary']['average_clang_score']:.1f}/100")
        print(f"score range: {report['benchmark_summary']['min_enhanced_score']:.1f} - {report['benchmark_summary']['max_enhanced_score']:.1f}")
        print(f"report saved: {filename}")

def main():
    parser = argparse.ArgumentParser(description='ai model evaluation pipeline')
    parser.add_argument('--benchmark', '-b', action='store_true', 
                       help='run full benchmark suite')
    parser.add_argument('--prompt', '-p', type=str, 
                       help='single prompt to evaluate')
    parser.add_argument('--model', '-m', type=str, default='mock',
                       choices=['mock', 'openai', 'gemini'],
                       help='ai model to use (mock/openai/gemini)')
    parser.add_argument('--api-key', type=str, 
                       help='api key for openai or gemini')
    parser.add_argument('--custom-prompts', nargs='+', 
                       help='multiple custom prompts')
    
    args = parser.parse_args()
    
    # initialize pipeline
    pipeline = AIEvaluationPipeline(
        model_type=args.model,
        api_key=args.api_key
    )
    
    if args.benchmark:
        pipeline.run_benchmark_suite()
    elif args.prompt:
        result = pipeline.run_single_evaluation(args.prompt)
        if result:
            score = result["enhanced_score"]
            clang_score = result.get('clang_analysis', {}).get('summary', {}).get('clang_score', 0)
            print(f"\nfinal results:")
            print(f"enhanced score: {score:.1f}/100")
            print(f"clang score: {clang_score:.1f}/100")
    elif args.custom_prompts:
        pipeline.run_custom_prompts(args.custom_prompts)
    else:
        print("ai model evaluation pipeline")
        print("usage examples:")
        print("  python ai_evaluation_pipeline.py --benchmark --model mock")
        print("  python ai_evaluation_pipeline.py --prompt 'create a character driver' --model gemini --api-key YOUR_KEY")
        print("  python ai_evaluation_pipeline.py --custom-prompts 'prompt1' 'prompt2' --model openai --api-key YOUR_KEY")
        print("\nsupported models: mock, openai, gemini")
        print("note: api key required for openai and gemini")

if __name__ == "__main__":
    main()
