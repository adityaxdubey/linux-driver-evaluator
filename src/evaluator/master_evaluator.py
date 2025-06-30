import sys
import json
import os
from datetime import datetime
from typing import Dict, List

sys.path.append('..')

from ..analyzers.clang_analyzer import EnhancedClangAnalyzer
from ..analyzers.runtime_tester import KernelModuleTester
from ..analyzers.performance_profiler import PerformanceProfiler
from ..analyzers.runtime_profiler import RuntimePerformanceProfiler
from ..analyzers.security_scanner import SecurityVulnerabilityScanner
from ..analyzers.static_analyzer import KernelCodeAnalyzer

class MasterDriverEvaluator:
    def __init__(self, kernel_headers_path: str = None):
        self.clang_analyzer = EnhancedClangAnalyzer(kernel_headers_path)
        self.runtime_tester = KernelModuleTester()
        self.performance_profiler = PerformanceProfiler()
        self.runtime_profiler = RuntimePerformanceProfiler()
        self.security_scanner = SecurityVulnerabilityScanner()
        self.fallback_analyzer = KernelCodeAnalyzer()
        
    def comprehensive_evaluation(self, code: str, prompt_info: Dict) -> Dict:
        print(f"running master evaluation for: {prompt_info.get('id', 'unknown')}")
        
        evaluation_result = {
            'metadata': {
                'prompt_id': prompt_info.get('id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'code_length': len(code),
                'analysis_modules': ['clang', 'runtime_compile', 'performance_static', 'runtime_perf', 'security']
            },
            'module_results': {},
            'integrated_scores': {},
            'overall_assessment': {}
        }
        
        # 1. Clang analysis
        print("1/5 running clang static analysis...")
        clang_results = self.clang_analyzer.analyze_code_detailed(code)
        evaluation_result['module_results']['clang'] = clang_results
        
        # 2. Runtime compilation test
        print("2/5 running runtime compilation test...")
        runtime_results = self.runtime_tester.test_module_compilation(code)
        evaluation_result['module_results']['runtime'] = runtime_results

        # 3. Performance static analysis
        print("3/5 running static performance analysis...")
        performance_results = self.performance_profiler.analyze_performance_patterns(code)
        evaluation_result['module_results']['performance'] = performance_results
        
        # 4. Runtime performance profiling
        print("4/5 running runtime performance profiling...")
        runtime_perf_results = self.runtime_profiler.analyze_runtime_performance(code)
        evaluation_result['module_results']['runtime_performance'] = runtime_perf_results
        
        # 5. Security scanning
        print("5/5 running security vulnerability scan...")
        security_results = self.security_scanner.scan_vulnerabilities(code)
        evaluation_result['module_results']['security'] = security_results
        
        # Integrate all scores
        evaluation_result['integrated_scores'] = self._calculate_integrated_scores(evaluation_result['module_results'])
        evaluation_result['overall_assessment'] = self._generate_overall_assessment(evaluation_result)
        self._save_comprehensive_report(evaluation_result)
        return evaluation_result
    
    def _calculate_integrated_scores(self, module_results: Dict) -> Dict:
        clang_score = module_results.get('clang', {}).get('summary', {}).get('clang_score', 0)
        runtime_score = 100 if module_results.get('runtime', {}).get('compilation_success', False) else 0
        performance_score = module_results.get('performance', {}).get('performance_score', 0)
        runtime_perf_score = module_results.get('runtime_performance', {}).get('runtime_performance_score', 0)
        security_score = module_results.get('security', {}).get('security_score', 0)
        
        # Adjust weights as needed based on what you want to emphasize
        weights = {
            'security': 0.27,
            'runtime_compile': 0.18,
            'clang': 0.18,
            'performance_static': 0.17,
            'runtime_perf': 0.20,
        }
        overall_score = (
            security_score * weights['security'] +
            runtime_score * weights['runtime_compile'] +
            clang_score * weights['clang'] +
            performance_score * weights['performance_static'] +
            runtime_perf_score * weights['runtime_perf']
        )
        return {
            'individual_scores': {
                'clang_static_analysis': clang_score,
                'runtime_compilation': runtime_score,
                'performance_static': performance_score,
                'runtime_performance': runtime_perf_score,
                'security_analysis': security_score
            },
            'weights_used': weights,
            'overall_score': round(overall_score, 2),
            'grade': self._score_to_grade(overall_score)
        }
    
    def _generate_overall_assessment(self, evaluation_result: Dict) -> Dict:
        overall_score = evaluation_result['integrated_scores']['overall_score']
        module_results = evaluation_result['module_results']
        if overall_score >= 90:
            quality_level = "production_ready"
            summary = "Excellent quality, safe for deployment"
        elif overall_score >= 75:
            quality_level = "good_with_minor_issues"
            summary = "Mostly solid, needs small improvements"
        elif overall_score >= 60:
            quality_level = "needs_improvement"
            summary = "Needs fixes before deployment"
        else:
            quality_level = "poor"
            summary = "Major issues, not safe for use"
        priority_actions = []
        # Security first
        security_vulns = module_results.get('security', {}).get('total_vulnerabilities', 0)
        if security_vulns > 0:
            priority_actions.append({'priority': 'critical', 'category': 'security', 'action': f"fix {security_vulns} security vulnerabilities"})
        if not module_results.get('runtime', {}).get('compilation_success', False):
            priority_actions.append({'priority': 'critical', 'category': 'compilation', 'action': "fix compilation errors"})
        if module_results.get('performance', {}).get('performance_score', 100) < 70:
            priority_actions.append({'priority': 'important', 'category': 'performance', 'action': "address performance issues"})
        if module_results.get('clang', {}).get('summary', {}).get('total_issues', 0) > 10:
            priority_actions.append({'priority': 'moderate', 'category': 'code_quality', 'action': "address code quality issues"})
        return {
            'quality_level': quality_level,
            'summary': summary,
            'overall_score': overall_score,
            'priority_actions': priority_actions,
            'deployment_recommendation': self._get_deployment_recommendation(overall_score),
            'next_steps': self._get_next_steps(priority_actions)
        }
    
    def _score_to_grade(self, score: float) -> str:
        if score >= 95: return "a+"
        elif score >= 90: return "a"
        elif score >= 85: return "b+"
        elif score >= 80: return "b"
        elif score >= 75: return "c+"
        elif score >= 70: return "c"
        elif score >= 65: return "d+"
        elif score >= 60: return "d"
        else: return "f"
    
    def _get_deployment_recommendation(self, score: float) -> str:
        if score >= 85:
            return "approved_for_production"
        elif score >= 70:
            return "approved_for_testing_with_monitoring"
        elif score >= 60:
            return "development_only_fix_issues_first"
        else:
            return "not_recommended_major_rework_needed"
    
    def _get_next_steps(self, priority_actions: List[Dict]) -> List[str]:
        if not priority_actions:
            return ["code quality is excellent, consider adding documentation"]
        steps = []
        critical = [a for a in priority_actions if a['priority'] == 'critical']
        important = [a for a in priority_actions if a['priority'] == 'important']
        if critical:
            steps.append(f"immediately address {len(critical)} critical issues")
        if important:
            steps.append(f"plan to fix {len(important)} important issues")
        steps.append("rerun evaluation after fixes")
        steps.append("consider peer code review")
        return steps
    
    def _save_comprehensive_report(self, evaluation_result: Dict):
        os.makedirs('results', exist_ok=True)
        filename = f"results/comprehensive_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(evaluation_result, f, indent=2)
        print(f"comprehensive report saved: {filename}")
