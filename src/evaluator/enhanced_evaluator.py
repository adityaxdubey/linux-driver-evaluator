import sys
import tempfile
import os
from typing import Dict,List
sys.path.append('..')

from ..analyzers.advanced_analyzer import KernelASTAnalyzer
from ..analyzers.runtime_monitor import KernelRuntimeMonitor
from ..analyzers.clang_analyzer import ClangTidyAnalyzer
from ..analyzers.static_analyzer import KernelCodeAnalyzer  # fallback

class EnhancedDriverEvaluator:
    def __init__(self):
        self.ast_analyzer = KernelASTAnalyzer()
        self.runtime_monitor = KernelRuntimeMonitor()
        self.clang_analyzer = ClangTidyAnalyzer()
        self.fallback_analyzer = KernelCodeAnalyzer()
        
    def comprehensive_evaluation(self, code: str, prompt_info: Dict) -> Dict:
        """run comprehensive evaluation with ast, clang, and runtime analysis"""
        
        print(f"running enhanced evaluation for: {prompt_info.get('id', 'unknown')}")
        
        results = {
            'metadata': {
                'prompt_id': prompt_info.get('id', 'unknown'),
                'analysis_type': 'enhanced_comprehensive',
                'code_length': len(code),
                'clang_available': self.clang_analyzer.clang_available
            }
        }
        
        # clang static analysis (primary)
        print("running clang-tidy analysis...")
        clang_results = self.clang_analyzer.analyze_code(code)
        results['clang_analysis'] = clang_results
        
        # ast-based static analysis  
        print("running semantic analysis...")
        ast_results = self.ast_analyzer.analyze_ast(code)
        results['ast_analysis'] = ast_results
        
        # runtime performance analysis
        print("analyzing runtime characteristics...")
        runtime_results = self.runtime_monitor.analyze_runtime_performance(code)
        results['runtime_analysis'] = runtime_results
        
        # fallback analysis if both clang and ast fail
        if ('error' in clang_results and 'error' in ast_results):
            print("primary analysis failed, using fallback...")
            fallback_results = self.fallback_analyzer.analyze_file(self._save_temp_file(code))
            results['fallback_analysis'] = fallback_results
        
        # calculate enhanced comprehensive score
        results['enhanced_score'] = self._calculate_enhanced_score(results)
        
        # generate detailed report
        results['detailed_report'] = self._generate_detailed_report(results)
        
        return results
    
    def _save_temp_file(self, code: str) -> str:
        """save code to temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            return f.name
    
    def _calculate_enhanced_score(self, results: Dict) -> float:
        """calculate enhanced quality score with clang integration"""
        
        clang_results = results.get('clang_analysis', {})
        ast_results = results.get('ast_analysis', {})
        runtime_results = results.get('runtime_analysis', {})
        
        # scoring weights
        weights = {
            'clang': 0.40,      # clang-tidy gets highest weight
            'security': 0.25,   # security from ast analysis
            'performance': 0.15, # performance from ast + runtime
            'memory': 0.10,     # memory management
            'compliance': 0.10  # kernel compliance
        }
        
        # clang score
        clang_score = 70  # default if clang unavailable
        if 'error' not in clang_results and clang_results.get('analysis_successful'):
            clang_score = clang_results.get('summary', {}).get('clang_score', 70)
        
        # ast-based scores
        security_score = 70
        performance_score = 70
        memory_score = 70
        compliance_score = 70
        
        if 'error' not in ast_results:
            security_score = 100 - ast_results.get('security_analysis', {}).get('risk_score', 30)
            performance_score = ast_results.get('performance_analysis', {}).get('performance_score', 70)
            memory_score = ast_results.get('memory_analysis', {}).get('memory_score', 70)
            compliance_score = ast_results.get('kernel_compliance', {}).get('compliance_score', 0) / 45 * 100
        
        # runtime performance boost
        runtime_score = runtime_results.get('performance_score', 70)
        performance_score = (performance_score + runtime_score) / 2
        
        # calculate weighted score
        enhanced_score = (
            clang_score * weights['clang'] +
            security_score * weights['security'] +
            performance_score * weights['performance'] +
            memory_score * weights['memory'] +
            compliance_score * weights['compliance']
        )
        
        return round(enhanced_score, 2)
    
    def _generate_detailed_report(self, results: Dict) -> Dict:
        """generate detailed analysis report"""
        
        report = {
            'executive_summary': self._generate_executive_summary(results),
            'detailed_findings': self._extract_detailed_findings(results),
            'recommendations': self._generate_comprehensive_recommendations(results)
        }
        
        return report
    
    def _generate_executive_summary(self, results: Dict) -> Dict:
        """generate executive summary"""
        
        clang_results = results.get('clang_analysis', {})
        ast_results = results.get('ast_analysis', {})
        
        summary = {
            'overall_quality': 'excellent' if results['enhanced_score'] >= 90 else 
                              'good' if results['enhanced_score'] >= 75 else
                              'fair' if results['enhanced_score'] >= 60 else 'poor',
            'primary_strengths': [],
            'primary_concerns': [],
            'clang_analysis_status': 'completed' if clang_results.get('analysis_successful') else 'unavailable'
        }
        
        # identify strengths
        if clang_results.get('summary', {}).get('clang_score', 0) >= 85:
            summary['primary_strengths'].append('passes professional static analysis')
        
        if ast_results.get('security_analysis', {}).get('risk_score', 100) <= 20:
            summary['primary_strengths'].append('minimal security vulnerabilities')
        
        if ast_results.get('memory_analysis', {}).get('memory_score', 0) >= 90:
            summary['primary_strengths'].append('excellent memory management')
        
        # identify concerns
        if clang_results.get('summary', {}).get('by_severity', {}).get('error', 0) > 0:
            summary['primary_concerns'].append('clang-tidy errors detected')
        
        if ast_results.get('security_analysis', {}).get('total_issues', 0) > 3:
            summary['primary_concerns'].append('multiple security issues')
        
        return summary
    
    def _extract_detailed_findings(self, results: Dict) -> Dict:
        """extract detailed findings from all analyzers"""
        
        findings = {
            'clang_findings': self._extract_clang_findings(results.get('clang_analysis', {})),
            'security_findings': self._extract_security_findings(results.get('ast_analysis', {})),
            'performance_findings': self._extract_performance_findings(results),
            'compliance_findings': self._extract_compliance_findings(results.get('ast_analysis', {}))
        }
        
        return findings
    
    def _extract_clang_findings(self, clang_results: Dict) -> Dict:
        """extract clang-specific findings"""
        if 'error' in clang_results:
            return {'status': 'unavailable', 'reason': clang_results['error']}
        
        return {
            'status': 'completed',
            'total_issues': clang_results.get('summary', {}).get('total_issues', 0),
            'by_severity': clang_results.get('summary', {}).get('by_severity', {}),
            'by_category': clang_results.get('summary', {}).get('by_category', {}),
            'score': clang_results.get('summary', {}).get('clang_score', 0)
        }
    
    def _extract_security_findings(self, ast_results: Dict) -> Dict:
        """extract security findings"""
        if 'error' in ast_results:
            return {'status': 'unavailable'}
        
        security = ast_results.get('security_analysis', {})
        return {
            'status': 'completed',
            'total_issues': security.get('total_issues', 0),
            'risk_score': security.get('risk_score', 0),
            'by_severity': security.get('by_severity', {})
        }
    
    def _extract_performance_findings(self, results: Dict) -> Dict:
        """extract performance findings"""
        ast_results = results.get('ast_analysis', {})
        runtime_results = results.get('runtime_analysis', {})
        
        return {
            'ast_performance_score': ast_results.get('performance_analysis', {}).get('performance_score', 0),
            'runtime_performance_score': runtime_results.get('performance_score', 0),
            'memory_operations': runtime_results.get('memory_operations', 0),
            'estimated_memory_usage': runtime_results.get('estimated_memory_usage', 0)
        }
    
    def _extract_compliance_findings(self, ast_results: Dict) -> Dict:
        """extract compliance findings"""
        if 'error' in ast_results:
            return {'status': 'unavailable'}
        
        compliance = ast_results.get('kernel_compliance', {})
        return {
            'status': 'completed',
            'score': compliance.get('compliance_score', 0),
            'max_score': compliance.get('max_compliance_score', 45)
        }
    
    def _generate_comprehensive_recommendations(self, results: Dict) -> List[str]:
        """generate comprehensive recommendations"""
        recommendations = []
        
        clang_results = results.get('clang_analysis', {})
        ast_results = results.get('ast_analysis', {})
        
        # clang-based recommendations
        if clang_results.get('analysis_successful'):
            clang_summary = clang_results.get('summary', {})
            
            if clang_summary.get('by_severity', {}).get('error', 0) > 0:
                recommendations.append("fix clang-tidy errors for production readiness")
            
            if clang_summary.get('by_category', {}).get('security', 0) > 0:
                recommendations.append("address security-related clang-tidy warnings")
            
            if clang_summary.get('by_category', {}).get('performance', 0) > 2:
                recommendations.append("optimize code based on clang performance suggestions")
        
        # ast-based recommendations  
        if 'error' not in ast_results:
            security = ast_results.get('security_analysis', {})
            if security.get('total_issues', 0) > 0:
                recommendations.append("resolve security vulnerabilities identified in semantic analysis")
        
        # general recommendations
        if results['enhanced_score'] < 75:
            recommendations.append("consider code review and refactoring for better quality")
        
        return recommendations[:8]
