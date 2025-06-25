# cli_evaluator.py
#!/usr/bin/env python3
"""
Linux Device Driver Code Evaluator CLI
Usage: python cli_evaluator.py [options]
"""

import argparse
import sys
import os
import json
from typing import List, Dict

# Add src to path
sys.path.append('src')
sys.path.append('.')

from src.evaluator.main_evaluator import DriverModelEvaluator
from tests.test_cases.sample_prompts import SAMPLE_PROMPTS, SAMPLE_CODES

class CLIEvaluator:
    def __init__(self):
        self.evaluator = DriverModelEvaluator()
    
    def evaluate_file(self, filepath: str, prompt_id: str = None, model_name: str = "manual"):
        """Evaluate a single code file"""
        
        if not os.path.exists(filepath):
            print(f"❌ Error: File {filepath} not found!")
            return
        
        # Read code from file
        try:
            with open(filepath, 'r') as f:
                code = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
            return
        
        # Find prompt info or create default
        prompt_info = {'id': prompt_id or 'manual_test', 'difficulty': 'unknown'}
        
        if prompt_id:
            for prompt in SAMPLE_PROMPTS:
                if prompt['id'] == prompt_id:
                    prompt_info = prompt
                    break
        
        # Evaluate
        result = self.evaluator.evaluate_single_code(code, prompt_info, model_name)
        
        # Print summary
        self._print_evaluation_summary(result)
    
    def evaluate_code_string(self, code: str, prompt_id: str = None, model_name: str = "manual"):
        """Evaluate code from string"""
        
        prompt_info = {'id': prompt_id or 'manual_test', 'difficulty': 'unknown'}
        
        if prompt_id:
            for prompt in SAMPLE_PROMPTS:
                if prompt['id'] == prompt_id:
                    prompt_info = prompt
                    break
        
        result = self.evaluator.evaluate_single_code(code, prompt_info, model_name)
        self._print_evaluation_summary(result)
    
    def run_sample_tests(self):
        """Run evaluation on built-in sample codes"""
        
        print("🧪 Running Sample Test Cases")
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
        
        print(f"\n📊 Sample Test Results:")
        print(f"Average Score: {report['overall_performance']['average_score']:.2f}")
        print(f"Score Range: {report['overall_performance']['min_score']:.2f} - {report['overall_performance']['max_score']:.2f}")
    
    def list_prompts(self):
        """List available sample prompts"""
        
        print("\n📋 Available Sample Prompts:")
        print("=" * 40)
        
        for i, prompt in enumerate(SAMPLE_PROMPTS, 1):
            print(f"{i}. ID: {prompt['id']}")
            print(f"   Difficulty: {prompt['difficulty']}")
            print(f"   Description: {prompt['prompt'][:100]}...")
            print()
    
    def _print_evaluation_summary(self, result: Dict):
        """Print evaluation summary"""
        
        print("\n📊 Evaluation Results")
        print("=" * 50)
        
        metadata = result['metadata']
        scores = result['scores']
        
        print(f"Prompt ID: {metadata['prompt_id']}")
        print(f"Model: {metadata['model_name']}")
        print(f"Code Length: {metadata['code_length']} characters")
        print()
        
        print(f"🎯 Overall Score: {scores['overall_score']:.2f}/100")
        print()
        
        print("📈 Category Scores:")
        for category, score in scores.get('category_scores', {}).items():
            print(f"  {category.replace('_', ' ').title()}: {score:.1f}/100")
        
        print()
        
        # Print key findings
        analysis = result['analysis_details']
        
        if 'compilation' in analysis:
            comp = analysis['compilation']
            status = "✅ PASS" if comp.get('success') else "❌ FAIL"
            print(f"🔧 Compilation: {status}")
            if comp.get('warnings', 0) > 0:
                print(f"  Warnings: {comp['warnings']}")
            if comp.get('errors', 0) > 0:
                print(f"  Errors: {comp['errors']}")
        
        if 'security' in analysis:
            sec = analysis['security']
            if sec.get('issues_found', 0) > 0:
                print(f"🛡️ Security Issues Found: {sec['issues_found']}")
                for issue in sec.get('issues', [])[:3]:  # Show first 3
                    print(f"  - {issue}")
        
        print()

def main():
    parser = argparse.ArgumentParser(description='Linux Device Driver Code Evaluator')
    parser.add_argument('--file', '-f', help='Evaluate code from file')
    parser.add_argument('--prompt-id', '-p', help='Specify prompt ID for context')
    parser.add_argument('--model', '-m', default='manual', help='Model name for tracking')
    parser.add_argument('--sample-tests', '-s', action='store_true', help='Run built-in sample tests')
    parser.add_argument('--list-prompts', '-l', action='store_true', help='List available prompts')
    parser.add_argument('--code', '-c', help='Evaluate code from command line string')
    
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
        print("Linux Device Driver Code Evaluator")
        print("Use --help for usage information")
        print("\nQuick start:")
        print("  python cli_evaluator.py --sample-tests")
        print("  python cli_evaluator.py --list-prompts")
        print("  python cli_evaluator.py --file mydriver.c")

if __name__ == "__main__":
    main()
