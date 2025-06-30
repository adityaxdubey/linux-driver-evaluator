"""
Ultimate Linux Driver Evaluation CLI: static, runtime, and LLM-based assessment.
"""
import argparse
import sys
import os
import json
from datetime import datetime

sys.path.append('src')
from src.evaluator.master_evaluator import MasterDriverEvaluator
from src.analyzers.ast_static_analyzer import AdvancedStaticAnalyzer
from src.evaluator.llm_evaluator import LLMBasedEvaluator
from src.ai_integration.model_client import MultiModelClient
from tests.test_cases.sample_prompts import SAMPLE_PROMPTS

def format_section(title):
    print("\n" + title)
    print("-" * len(title))

class UnifiedCLI:
    def __init__(self, args):
        self.args = args
        self.evaluator = MasterDriverEvaluator(args.kernel_headers)
        self.ast_analyzer = AdvancedStaticAnalyzer()
        self.llm_eval = LLMBasedEvaluator()

    def run(self):
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
        with open(filepath, 'r') as f:
            code = f.read()

        # Optional: load associated prompt/metadata for LLM evaluation
        prompt_info = {
            'id': self.args.prompt_id or os.path.basename(filepath),
            'llm_generated': bool(self.args.llm_metadata),
            'prompt': self.args.prompt if hasattr(self.args, 'prompt') else "",
            'model_metadata': (json.loads(self.args.llm_metadata)
                                if self.args.llm_metadata else {})
        }

        print(f"Comprehensive evaluation of {filepath}")
        print("=" * 60)

        results = self.evaluator.comprehensive_evaluation(code, prompt_info)

        # Run advanced static analysis and LLM evaluation
        static_results = self.ast_analyzer.deep_static_analysis(code)
        results['module_results']['advanced_static'] = static_results
        if prompt_info['llm_generated']:
            llm_results = self.llm_eval.evaluate_generated_code(
                code, prompt_info.get('prompt', ''), prompt_info.get('model_metadata', {}))
            results['module_results']['llm'] = llm_results

        if self.args.detailed:
            self._print_detailed_results(results)
        else:
            self._print_summary_results(results)

    def run_ai_benchmark(self):
        model_type = self.args.model
        api_key = self.args.api_key or os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')
        if model_type != 'mock' and not api_key:
            print(f"Error: API key required for '{model_type}'.")
            sys.exit(1)
        ai_client = MultiModelClient(model_type, api_key)
        print(f"Running AI Benchmark Suite with '{model_type}' model...")
        print("=" * 60)
        for i, prompt_data in enumerate(SAMPLE_PROMPTS, 1):
            print(f"\n[{i}/{len(SAMPLE_PROMPTS)}] Generating code for prompt: {prompt_data['id']}")
            gen_result = ai_client.generate_driver_code(prompt_data['prompt'])
            if not gen_result['success']:
                print(f"  -> Generation failed: {gen_result.get('error', 'Unknown error')}")
                continue
            code = gen_result['code']
            prompt_info = {
                'id': prompt_data['id'],
                'prompt': prompt_data['prompt'],
                'llm_generated': True,
                'model_metadata': {
                    'model': gen_result.get('model'),
                    'tokens_used': gen_result.get('tokens_used')
                }
            }
            results = self.evaluator.comprehensive_evaluation(code, prompt_info)
            static_results = self.ast_analyzer.deep_static_analysis(code)
            results['module_results']['advanced_static'] = static_results
            llm_results = self.llm_eval.evaluate_generated_code(
                code, prompt_data['prompt'], prompt_info['model_metadata'])
            results['module_results']['llm'] = llm_results
            score = results.get('integrated_scores', {}).get('overall_score', 0)
            print(f"  -> Evaluation Complete. Overall Score: {score:.1f}/100")

    def _print_summary_results(self, results: dict):
        integrated = results.get('integrated_scores', {})
        assessment = results.get('overall_assessment', {})
        format_section("Executive Summary")
        print(f"Overall Score: {integrated.get('overall_score', 0):.1f}/100 (Grade: {integrated.get('grade', 'N/A')})")
        print(f"Quality Level: {assessment.get('quality_level', 'unknown')}")
        print(f"Deployment Recommendation: {assessment.get('deployment_recommendation', 'unknown')}\n")
        print("Module Scores:")
        for module, score in integrated.get('individual_scores', {}).items():
            print(f"  - {module.replace('_', ' ').title()}: {score:.1f}/100")
        if assessment.get('priority_actions'):
            print("\nPriority Actions:")
            for action in assessment['priority_actions'][:3]:
                print(f"  - {action['priority'].upper()}: {action['action']}")

    def _print_detailed_results(self, results: dict):
        self._print_summary_results(results)
        format_section("Detailed Analysis")
        modules = results.get('module_results', {})

        # Clang Analysis
        clang = modules.get('clang', {})
        if 'summary' in clang:
            summary = clang['summary']
            print("\n[Clang Static Analysis]")
            print(f"  Total Issues: {summary.get('total_issues', 0)}")
            print(f"  By Severity: {summary.get('by_severity', {})}")

        # Advanced Static Analysis
        adv_static = modules.get('advanced_static', {})
        if adv_static:
            print("\n[Advanced Static Analysis]")
            for key, val in adv_static.items():
                if isinstance(val, dict) or isinstance(val, list):
                    print(f"  {key}: {str(val)[:120]}")
                else:
                    print(f"  {key}: {val}")

        # Runtime Testing
        runtime = modules.get('runtime', {})
        print("\n[Runtime Compilation Test]")
        print(f"  Compilation: {'Success' if runtime.get('compilation_success') else 'Failed'}")

        # Performance Analysis
        perf = modules.get('performance', {})
        print("\n[Performance Analysis]")
        print(f"  Static Score: {perf.get('performance_score', 0):.1f}/100")
        rt_perf = modules.get('runtime_performance', {})
        if rt_perf:
            print(f"  Runtime Score: {rt_perf.get('runtime_performance_score', 0):.1f}/100")
            print(f"  Execution Time (us): {rt_perf.get('runtime_metrics', {}).get('execution_time_us')}")
            print(f"  Memory Metrics: {rt_perf.get('runtime_metrics', {}).get('memory_analysis', {})}")

        # Security Scan
        sec = modules.get('security', {})
        print("\n[Security Vulnerability Scan]")
        print(f"  Vulnerabilities Found: {sec.get('total_vulnerabilities', 0)}")
        print(f"  Security Score: {sec.get('security_score', 0):.1f}/100")

        # LLM Evaluation (if present)
        llm = modules.get('llm', {})
        if llm:
            print("\n[LLM-Based Evaluation]")
            for key, val in llm.items():
                if isinstance(val, dict) or isinstance(val, list):
                    print(f"  {key}: {str(val)[:120]}")
                else:
                    print(f"  {key}: {val}")

def create_parser():
    parser = argparse.ArgumentParser(
        description="Ultimate Linux Driver Evaluation System",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a driver file')
    eval_parser.add_argument('file', help='Driver code file to evaluate')
    eval_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed results')
    eval_parser.add_argument('--kernel-headers', help='Kernel headers path')
    eval_parser.add_argument('--prompt-id', help='Evaluation run ID')
    # Optional: LLM prompt and metadata for LLM evaluation
    eval_parser.add_argument('--prompt', help='Prompt for LLM-based evaluation')
    eval_parser.add_argument('--llm-metadata', help='JSON string with LLM metadata (model, tokens, etc)')

    # AI Benchmark Command
    ai_parser = subparsers.add_parser('ai-benchmark', help='Benchmark with AI-generated code')
    ai_parser.add_argument('--model', choices=['mock', 'openai', 'gemini'], default='mock', help='AI model')
    ai_parser.add_argument('--api-key', help='API key for AI model')
    ai_parser.add_argument('--kernel-headers', help='Kernel headers path')

    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    cli = UnifiedCLI(args)
    cli.run()
