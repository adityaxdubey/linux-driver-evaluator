import argparse
import sys
import os
import json

sys.path.append('src')
from src.evaluator.master_evaluator import MasterDriverEvaluator
from src.ai_integration.model_client import MultiModelClient
from tests.test_cases.sample_prompts import SAMPLE_PROMPTS

class UnifiedCLI:
    def __init__(self, args):
        self.args = args
        self.evaluator = MasterDriverEvaluator(args.kernel_headers)

    def run(self):
        """Dispatch to the correct function based on the command."""
        if self.args.command == 'evaluate':
            self.evaluate_file()
        elif self.args.command == 'ai-benchmark':
            self.run_ai_benchmark()
        else:
            print(f"Unknown command: {self.args.command}")
            sys.exit(1)

    def evaluate_file(self):
        filepath = self.args.file
        if not os.path.exists(filepath):
            print(f"Error: File not found - {filepath}")
            sys.exit(1)

        try:
            with open(filepath, 'r') as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

        prompt_info = {'id': self.args.prompt_id or os.path.basename(filepath)}
        
        print(f"Running comprehensive evaluation on {filepath}...")
        print("=" * 60)
        results = self.evaluator.comprehensive_evaluation(code, prompt_info)
        
        if self.args.detailed:
            self._print_detailed_results(results)
        else:
            self._print_summary_results(results)

    def run_ai_benchmark(self):
        model_type = self.args.model
        api_key = self.args.api_key or os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')

        if model_type != 'mock' and not api_key:
            print(f"Error: API key must be provided for '{model_type}' model via --api-key or environment variable.")
            sys.exit(1)

        ai_client = MultiModelClient(model_type, api_key)

        print(f"Running AI Benchmark Suite with '{model_type}' model...")
        print("=" * 60)

        for i, prompt_data in enumerate(SAMPLE_PROMPTS, 1):
            print(f"\n[{i}/{len(SAMPLE_PROMPTS)}] Generating code for prompt: {prompt_data['id']}")
            generation_result = ai_client.generate_driver_code(prompt_data['prompt'])

            if not generation_result['success']:
                print(f"  -> Failed to generate code: {generation_result.get('error', 'Unknown error')}")
                continue
            
            print(f"  -> Code generated successfully. Evaluating...")
            code = generation_result['code']
            results = self.evaluator.comprehensive_evaluation(code, prompt_data)
            
            score = results.get('integrated_scores', {}).get('overall_score', 0)
            print(f"  -> Evaluation Complete. Overall Score: {score:.1f}/100")

    def _print_summary_results(self, results: dict):
        integrated = results.get('integrated_scores', {})
        assessment = results.get('overall_assessment', {})
        
        print("\n--- Executive Summary ---")
        print(f"Overall Score: {integrated.get('overall_score', 0):.1f}/100 (Grade: {integrated.get('grade', 'N/A')})")
        print(f"Quality Level: {assessment.get('quality_level', 'unknown')}")
        print(f"Deployment Recommendation: {assessment.get('deployment_recommendation', 'unknown')}")
        
        print("\nModule Scores:")
        for module, score in integrated.get('individual_scores', {}).items():
            print(f"  - {module.replace('_', ' ').title()}: {score:.1f}/100")
        
        if assessment.get('priority_actions'):
            print("\nPriority Actions:")
            for action in assessment['priority_actions'][:3]:
                print(f"  - {action['priority'].upper()}: {action['action']}")

    def _print_detailed_results(self, results: dict):
        self._print_summary_results(results)
        
        print("\n--- Detailed Analysis ---")
        modules = results.get('module_results', {})

        # Clang Analysis
        clang = modules.get('clang', {})
        if 'summary' in clang:
            summary = clang['summary']
            print("\n[Clang Static Analysis]")
            print(f"  Total Issues: {summary.get('total_issues', 0)}")
            print(f"  By Severity: {summary.get('by_severity', {})}")

        # Runtime Testing
        runtime = modules.get('runtime', {})
        print("\n[Runtime Compilation Test]")
        print(f"  Compilation: {'Success' if runtime.get('compilation_success') else 'Failed'}")
        
        # Performance Analysis
        perf = modules.get('performance', {})
        print("\n[Performance Analysis]")
        print(f"  Score: {perf.get('performance_score', 0):.1f}/100")
        
        # Security Scan
        sec = modules.get('security', {})
        print("\n[Security Vulnerability Scan]")
        print(f"  Vulnerabilities Found: {sec.get('total_vulnerabilities', 0)}")
        print(f"  Security Score: {sec.get('security_score', 0):.1f}/100")


def create_parser():
    parser = argparse.ArgumentParser(
        description="The Ultimate Linux Driver Evaluation System.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # 'evaluate' command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a single driver file.')
    eval_parser.add_argument('file', help='Path to the driver file to evaluate.')
    eval_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed analysis results.')
    eval_parser.add_argument('--kernel-headers', help='Base path to kernel headers (e.g., /usr/src/linux-headers-$(uname -r))')
    eval_parser.add_argument('--prompt-id', help='An optional ID for this evaluation run.')

    # 'ai-benchmark' command
    ai_parser = subparsers.add_parser('ai-benchmark', help='Run a benchmark using an AI model to generate code.')
    ai_parser.add_argument('--model', choices=['mock', 'openai', 'gemini'], default='mock', help='AI model to use.')
    ai_parser.add_argument('--api-key', help='API key for the selected AI model.')
    ai_parser.add_argument('--kernel-headers', help='Base path to kernel headers for evaluating generated code.')

    return parser

if __name__ == "__main__":
    main_parser = create_parser()
    args = main_parser.parse_args()
    cli = UnifiedCLI(args)
    cli.run()
