import argparse
import sys
import os
import json
from typing import Dict
sys.path.append('src')
from src.evaluator.master_evaluator import MasterDriverEvaluator

class UltimateDriverEvaluator:
    def __init__(self, kernel_headers: str = None):
        self.evaluator = MasterDriverEvaluator(kernel_headers)
    
    def evaluate_file(self, filepath: str, prompt_id: str = None, detailed: bool = False):
        """evaluate driver file with all analysis modules"""
        
        if not os.path.exists(filepath):
            print(f"error: file not found - {filepath}")
            return
        
        try:
            with open(filepath, 'r') as f:
                code = f.read()
        except Exception as e:
            print(f"error reading file: {str(e)}")
            return
        
        prompt_info = {'id': prompt_id or os.path.basename(filepath)}
        
        print(f"comprehensive evaluation of {filepath}")
        print("=" * 60)
        
        results = self.evaluator.comprehensive_evaluation(code, prompt_info)
        
        if detailed:
            self._print_detailed_results(results)
        else:
            self._print_summary_results(results)
    
    def _print_summary_results(self, results: Dict):
        """print executive summary"""
        
        integrated = results['integrated_scores']
        assessment = results['overall_assessment']
        
        print(f"\nexecutive summary")
        print("-" * 30)
        print(f"overall score: {integrated['overall_score']:.1f}/100 (grade: {integrated['grade']})")
        print(f"quality level: {assessment['quality_level']}")
        print(f"deployment: {assessment['deployment_recommendation']}")
        print()
        
        print("module scores:")
        for module, score in integrated['individual_scores'].items():
            print(f"  {module}: {score:.1f}/100")
        print()
        
        if assessment['priority_actions']:
            print("priority actions:")
            for action in assessment['priority_actions'][:3]:
                print(f"  {action['priority']}: {action['action']}")
        
        print(f"\nfull report: {results['metadata']['timestamp']}")
    
    def _print_detailed_results(self, results: Dict):
        """print comprehensive detailed results"""
        
        self._print_summary_results(results)
        
        print("\ndetailed analysis results")
        print("=" * 40)
        
        # clang analysis details
        clang = results['module_results'].get('clang', {})
        if 'summary' in clang:
            print(f"\nclang static analysis:")
            summary = clang['summary']
            print(f"  total issues: {summary.get('total_issues', 0)}")
            print(f"  critical issues: {summary.get('critical_issues', 0)}")
            print(f"  by severity: {summary.get('by_severity', {})}")
        
        # runtime testing details
        runtime = results['module_results'].get('runtime', {})
        print(f"\nruntime testing:")
        print(f"  compilation: {'success' if runtime.get('compilation_success') else 'failed'}")
        print(f"  module created: {'yes' if runtime.get('module_created') else 'no'}")
        
        # performance analysis details
        performance = results['module_results'].get('performance', {})
        print(f"\nperformance analysis:")
        print(f"  score: {performance.get('performance_score', 0):.1f}/100")
        if 'algorithmic_complexity' in performance:
            complexity = performance['algorithmic_complexity']
            print(f"  max nesting: {complexity.get('max_nesting_level', 0)}")
        
        # security scan details
        security = results['module_results'].get('security', {})
        print(f"\nsecurity analysis:")
        print(f"  vulnerabilities: {security.get('total_vulnerabilities', 0)}")
        print(f"  security score: {security.get('security_score', 0):.1f}/100")
        if security.get('by_severity'):
            print(f"  by severity: {security['by_severity']}")

def main():
    parser = argparse.ArgumentParser(description='ultimate linux driver evaluation system')
    parser.add_argument('file', help='driver file to evaluate')
    parser.add_argument('--kernel-headers', help='path to kernel headers')
    parser.add_argument('--detailed', '-d', action='store_true', help='detailed output')
    parser.add_argument('--prompt-id', help='prompt context id')
    
    args = parser.parse_args()
    
    evaluator = UltimateDriverEvaluator(args.kernel_headers)
    evaluator.evaluate_file(args.file, args.prompt_id, args.detailed)

if __name__ == "__main__":
    main()
