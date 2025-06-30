import argparse
import sys
import os
import json

sys.path.append('src')

from src.evaluator.enhanced_evaluator import EnhancedDriverEvaluator
from tests.test_cases.sample_prompts import SAMPLE_PROMPTS, SAMPLE_CODES

class ProductionEvaluator:
    def __init__(self):
        self.evaluator = EnhancedDriverEvaluator()
    
    def evaluate_file(self, filepath: str, prompt_id: str = None, detailed: bool = False):
        if not os.path.exists(filepath):
            print(f"error: file {filepath} not found")
            return
        
        try:
            with open(filepath, 'r') as f:
                code = f.read()
        except Exception as e:
            print(f"error reading file: {str(e)}")
            return
        
        prompt_info = {'id': prompt_id or 'manual_test', 'difficulty': 'unknown'}
        
        if prompt_id:
            for prompt in SAMPLE_PROMPTS:
                if prompt['id'] == prompt_id:
                    prompt_info = prompt
                    break
        
        result = self.evaluator.comprehensive_evaluation(code, prompt_info)
        
        if detailed:
            self._print_detailed_results(result)
        else:
            self._print_summary_results(result)
    
    def run_benchmark(self, detailed: bool = False):
        print("running professional benchmark suite")
        print("=" * 50)
        
        samples = [
            {'code': SAMPLE_CODES['good_basic_driver'], 'prompt_info': {'id': 'good_driver'}},
            {'code': SAMPLE_CODES['bad_basic_driver'], 'prompt_info': {'id': 'bad_driver'}}
        ]
        
        results = []
        for i, sample in enumerate(samples, 1):
            print(f"\nevaluating sample {i}/{len(samples)}: {sample['prompt_info']['id']}")
            result = self.evaluator.comprehensive_evaluation(sample['code'], sample['prompt_info'])
            results.append(result)
            
            score = result['enhanced_score']
            clang_score = result.get('clang_analysis', {}).get('summary', {}).get('clang_score', 0)
            print(f"  enhanced score: {score:.1f}/100")
            print(f"  clang score: {clang_score:.1f}/100")
        
        # summary
        avg_enhanced = sum(r['enhanced_score'] for r in results) / len(results)
        avg_clang = sum(r.get('clang_analysis', {}).get('summary', {}).get('clang_score', 0) for r in results) / len(results)
        
        print(f"\nbenchmark summary:")
        print(f"  average enhanced score: {avg_enhanced:.1f}/100")
        print(f"  average clang score: {avg_clang:.1f}/100")
    
    def _print_summary_results(self, result):
        print("\nevaluation summary")
        print("=" * 30)
        
        score = result['enhanced_score']
        clang_available = result['metadata']['clang_available']
        
        print(f"enhanced score: {score:.1f}/100")
        print(f"clang analysis: {'enabled' if clang_available else 'disabled'}")
        
        if clang_available:
            clang_summary = result.get('clang_analysis', {}).get('summary', {})
            print(f"clang score: {clang_summary.get('clang_score', 0):.1f}/100")
            print(f"clang issues: {clang_summary.get('total_issues', 0)}")
        
        # executive summary
        exec_summary = result.get('detailed_report', {}).get('executive_summary', {})
        quality = exec_summary.get('overall_quality', 'unknown')
        print(f"overall quality: {quality}")
        
        concerns = exec_summary.get('primary_concerns', [])
        if concerns:
            print("primary concerns:")
            for concern in concerns[:3]:
                print(f"  - {concern}")
    
    def _print_detailed_results(self, result):
        print("\ndetailed evaluation results")
        print("=" * 40)
        
        # basic info
        score = result['enhanced_score']
        metadata = result['metadata']
        print(f"enhanced score: {score:.2f}/100")
        print(f"prompt id: {metadata['prompt_id']}")
        print(f"code length: {metadata['code_length']} characters")
        print(f"clang available: {metadata['clang_available']}")
        
        # clang analysis
        clang_results = result.get('clang_analysis', {})
        if clang_results.get('analysis_successful'):
            clang_summary = clang_results.get('summary', {})
            print(f"\nclang-tidy analysis:")
            print(f"  total issues: {clang_summary.get('total_issues', 0)}")
            print(f"  clang score: {clang_summary.get('clang_score', 0):.1f}/100")
            
            by_severity = clang_summary.get('by_severity', {})
            print(f"  by severity: errors={by_severity.get('error', 0)}, warnings={by_severity.get('warning', 0)}")
            
            by_category = clang_summary.get('by_category', {})
            print(f"  by category: reliability={by_category.get('reliability', 0)}, general={by_category.get('general', 0)}")
        
        # semantic analysis
        ast_results = result.get('ast_analysis', {})
        if 'error' not in ast_results:
            security = ast_results.get('security_analysis', {})
            memory = ast_results.get('memory_analysis', {})
            print(f"\nsemantic analysis:")
            print(f"  security issues: {security.get('total_issues', 0)}")
            print(f"  memory score: {memory.get('memory_score', 0):.1f}/100")
        
        # recommendations
        recommendations = result.get('detailed_report', {}).get('recommendations', [])
        if recommendations:
            print(f"\nrecommendations:")
            for rec in recommendations[:5]:
                print(f"  - {rec}")

def main():
    parser = argparse.ArgumentParser(description='linux driver evaluation system')
    parser.add_argument('--file', '-f', help='evaluate driver file')
    parser.add_argument('--prompt-id', '-p', help='prompt context id')
    parser.add_argument('--benchmark', '-b', action='store_true', help='run benchmark suite')
    parser.add_argument('--detailed', '-d', action='store_true', help='detailed output')
    
    args = parser.parse_args()
    evaluator = ProductionEvaluator()
    
    if args.benchmark:
        evaluator.run_benchmark(args.detailed)
    elif args.file:
        evaluator.evaluate_file(args.file, args.prompt_id, args.detailed)
    else:
        print("linux driver code evaluation system")
        print("professional static analysis with clang-tidy integration")
        print()
        print("usage:")
        print("  python cli_final.py --file driver.c")
        print("  python cli_final.py --file driver.c --detailed")
        print("  python cli_final.py --benchmark")
        print("  python cli_final.py --benchmark --detailed")

if __name__ == "__main__":
    main()
