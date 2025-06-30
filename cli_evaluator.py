import argparse
import sys
import os
import json
from typing import Dict, List

sys.path.append('src')
sys.path.append('.')

from src.evaluator.main_evaluator import DriverModelEvaluator
from tests.test_cases.sample_prompts import SAMPLE_PROMPTS, SAMPLE_CODES

class CLIEvaluator:
    def __init__(self):
        self.evaluator = DriverModelEvaluator()
    
    def evaluate_file(self, filepath: str, prompt_id: str = None, model_name: str = "manual"):
        if not os.path.exists(filepath):
            print(f"error: file {filepath} not found!")
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
        
        result = self.evaluator.evaluate_single_code(code, prompt_info, model_name)
        self._print_evaluation_summary(result)
    
    def evaluate_code_string(self, code: str, prompt_id: str = None, model_name: str = "manual"):
        prompt_info = {'id': prompt_id or 'manual_test', 'difficulty': 'unknown'}
        
        if prompt_id:
            for prompt in SAMPLE_PROMPTS:
                if prompt['id'] == prompt_id:
                    prompt_info = prompt
                    break
        
        result = self.evaluator.evaluate_single_code(code, prompt_info, model_name)
        self._print_evaluation_summary(result)
    
    def run_sample_tests(self):
        print("running sample tests")
        print("=" * 50)
        
        samples = [
            {
                'code': SAMPLE_CODES['good_basic_driver'],
                'prompt_info': {'id': 'sample_good', 'difficulty': 'test'}
            },
            {
                'code': SAMPLE_CODES['bad_basic_driver'],
                'prompt_info': {'id': 'sample_bad', 'difficulty': 'test'}
            }
        ]
        
        report = self.evaluator.batch_evaluate(samples, "sample_test")
        
        print(f"\nsample test results:")
        print(f"avg score: {report['overall_performance']['average_score']:.2f}")
        print(f"score range: {report['overall_performance']['min_score']:.2f} - {report['overall_performance']['max_score']:.2f}")
    
    def list_prompts(self):
        print("\navailable sample prompts:")
        print("=" * 40)
        
        for i, prompt in enumerate(SAMPLE_PROMPTS, 1):
            print(f"{i}. id: {prompt['id']}")
            print(f"   difficulty: {prompt['difficulty']}")
            print(f"   desc: {prompt['prompt'][:100]}...")
            print()
    
    def _print_evaluation_summary(self, result: Dict):
        print("\nevaluation results")
        print("=" * 50)
        
        metadata = result['metadata']
        scores = result['scores']
        
        print(f"prompt id: {metadata['prompt_id']}")
        print(f"model: {metadata['model_name']}")
        print(f"code length: {metadata['code_length']} chars")
        print()
        
        overall = scores['overall_score']
        grade = self._get_grade(overall)
        print(f"overall score: {overall:.2f}/100 ({grade})")
        print()
        
        print("category scores:")
        for category, score in scores.get('category_scores', {}).items():
            print(f"  {category.replace('_', ' ').title()}: {score:.1f}/100")
        
        print()
        
        analysis = result['analysis_details']
        
        if 'compilation' in analysis:
            comp = analysis['compilation']
            status = "pass" if comp.get('success') else "fail"
            print(f"compilation: {status}")
            if comp.get('warnings', 0) > 0:
                print(f"  warnings: {comp['warnings']}")
            if comp.get('errors', 0) > 0:
                print(f"  errors: {comp['errors']}")
            if comp.get('basic_checks_passed'):
                print(f"  basic syntax: pass")
        
        if 'security' in analysis:
            sec = analysis['security']
            if sec.get('issues_found', 0) > 0:
                print(f"security issues found: {sec['issues_found']}")
                for issue in sec.get('issues', [])[:3]:
                    print(f"  - {issue}")
            else:
                print(f"security: no major issues found")
        
        if 'kernel_patterns' in analysis:
            patterns = analysis['kernel_patterns']
            if patterns.get('patterns_found', 0) > 0:
                print(f"\nkernel patterns found ({patterns['patterns_found']}):")
                for pattern in patterns.get('patterns', [])[:5]:
                    print(f"  - {pattern}") # Use hyphen for list
        
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\nrecommendations:")
            for rec in recommendations[:6]:
                print(f"  - {rec}") # Use hyphen for list
        
        print()
    
    def _get_grade(self, score: float) -> str:
        if score >= 90: return "a"
        elif score >= 80: return "b"
        elif score >= 70: return "c"
        elif score >= 60: return "d"
        else: return "f"
    
    def _get_progress_bar(self, score: float, width: int = 20) -> str:
        return "" 

def main():
    parser = argparse.ArgumentParser(description='linux driver code evaluator')
    parser.add_argument('--file', '-f', help='evaluate code from file')
    parser.add_argument('--prompt-id', '-p', help='prompt id for context')
    parser.add_argument('--model', '-m', default='manual', help='model name for tracking')
    parser.add_argument('--sample-tests', '-s', action='store_true', help='run built-in sample tests')
    parser.add_argument('--list-prompts', '-l', action='store_true', help='list available prompts')
    parser.add_argument('--code', '-c', help='evaluate code from command line string')
    
    args = parser.parse_args()
    
    cli = CLIEvaluator()
    
    if args.list_prompts:
        cli.list_prompts()
    elif args.sample_tests:
        cli.run_sample_tests()
    elif args.file:
        cli.evaluate_file(args.file, args.prompt_id, args.model)
    elif args.code:
        cli.evaluate_code_string(args.code, args.prompt_id, args.model)
    else:
        print("linux driver code evaluator")
        print("=" * 40)
        print("use --help for usage")
        print("\nquick start:")
        print("  python cli_evaluator.py --sample-tests")
        print("  python cli_evaluator.py --list-prompts")
        print("  python cli_evaluator.py --file mydriver.c")
        print("  python cli_evaluator.py --file test_driver.c --prompt-id basic_char_driver")

if __name__ == "__main__":
    main()
