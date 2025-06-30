import sys
import tempfile
import os
from typing import Dict
sys.path.append('..')

from ..analyzers.advanced_analyzer import KernelASTAnalyzer
from ..analyzers.runtime_monitor import KernelRuntimeMonitor
from ..analyzers.static_analyzer import KernelCodeAnalyzer  # fallback

class AdvancedDriverEvaluator:
    def __init__(self):
        self.ast_analyzer = KernelASTAnalyzer()
        self.runtime_monitor = KernelRuntimeMonitor()
        self.fallback_analyzer = KernelCodeAnalyzer()
        
    def comprehensive_evaluation(self, code: str, prompt_info: Dict) -> Dict:
        """run comprehensive evaluation with ast and runtime analysis"""
        
        print(f"running advanced evaluation for: {prompt_info.get('id', 'unknown')}")
        
        results = {
            'metadata': {
                'prompt_id': prompt_info.get('id', 'unknown'),
                'analysis_type': 'comprehensive',
                'code_length': len(code)
            }
        }
        
        # ast-based static analysis
        print("running ast analysis...")
        ast_results = self.ast_analyzer.analyze_ast(code)
        results['ast_analysis'] = ast_results
        
        # runtime performance analysis
        print("analyzing runtime characteristics...")
        runtime_results = self.runtime_monitor.analyze_runtime_performance(code)
        results['runtime_analysis'] = runtime_results
        
        # fallback to pattern-based analysis if ast fails
        if 'error' in ast_results:
            print("ast analysis failed, using fallback analyzer...")
            fallback_results = self.fallback_analyzer.analyze_file(self._save_temp_file(code))
            results['fallback_analysis'] = fallback_results
        
        # calculate comprehensive score
        results['comprehensive_score'] = self._calculate_comprehensive_score(results)
        
        # generate instrumented code for testing
        results['instrumented_code'] = self.runtime_monitor.generate_instrumented_code(code)
        results['test_suite'] = self.runtime_monitor.generate_test_suite(code)
        
        return results
    
    def _save_temp_file(self, code: str) -> str:
        """save code to temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            return f.name
    
    def _calculate_comprehensive_score(self, results: Dict) -> float:
        """calculate comprehensive quality score"""
        
        ast_results = results.get('ast_analysis', {})
        runtime_results = results.get('runtime_analysis', {})
        
        if 'error' in ast_results:
            # use fallback scoring
            fallback = results.get('fallback_analysis', {})
            return self._fallback_scoring(fallback)
        
        # weighted scoring from advanced analysis
        weights = {
            'security': 0.35,
            'performance': 0.25,
            'memory': 0.20,
            'compliance': 0.15,
            'runtime': 0.05
        }
        
        security_score = 100 - ast_results.get('security_analysis', {}).get('risk_score', 50)
        performance_score = ast_results.get('performance_analysis', {}).get('performance_score', 70)
        memory_score = ast_results.get('memory_analysis', {}).get('memory_score', 70)
        compliance_score = ast_results.get('kernel_compliance', {}).get('compliance_score', 0) / 35 * 100
        runtime_score = runtime_results.get('performance_score', 70)
        
        comprehensive_score = (
            security_score * weights['security'] +
            performance_score * weights['performance'] +
            memory_score * weights['memory'] +
            compliance_score * weights['compliance'] +
            runtime_score * weights['runtime']
        )
        
        return round(comprehensive_score, 2)
    
    def _fallback_scoring(self, fallback_results: Dict) -> float:
        """calculate score using fallback analyzer"""
        if not fallback_results:
            return 30.0
        
        compilation = fallback_results.get('compilation', {})
        security = fallback_results.get('security', {})
        
        base_score = 50
        if compilation.get('success', False):
            base_score += 20
        
        security_penalty = security.get('issues_found', 0) * 5
        base_score -= security_penalty
        
        return max(0, base_score)
