import os
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Any
import sys
sys.path.append('..')

from ..analyzers.static_analyzer import KernelCodeAnalyzer
from ..metrics.evaluation_metrics import DriverEvaluationMetrics

class DriverModelEvaluator:
    def __init__(self, output_dir: str = "results"):
        self.analyzer = KernelCodeAnalyzer()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.evaluation_history = []
    
    def evaluate_single_code(self, code: str, prompt_info: Dict, model_name: str = "unknown") -> Dict:
        """Evaluate a single piece of generated driver code"""
        
        print(f"\n🔍 Evaluating code for prompt: {prompt_info.get('id', 'unknown')}")
        
        # Create temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as temp_file:
            temp_file.write(code)
            temp_filepath = temp_file.name
        
        try:
            # Run static analysis
            print("  📊 Running static analysis...")
            analysis_results = self.analyzer.analyze_file(temp_filepath)
            
            # Calculate comprehensive metrics
            metrics = self._calculate_comprehensive_metrics(analysis_results, prompt_info)
            
            # Create evaluation result
            evaluation_result = {
                'metadata': {
                    'prompt_id': prompt_info.get('id', 'unknown'),
                    'model_name': model_name,
                    'timestamp': datetime.now().isoformat(),
                    'code_length': len(code),
                    'difficulty': prompt_info.get('difficulty', 'unknown')
                },
                'scores': {
                    'overall_score': metrics.calculate_overall_score(),
                    'detailed_metrics': metrics.metrics,
                    'category_scores': self._get_category_scores(metrics)
                },
                'analysis_details': analysis_results,
                'code_snippet': code[:500] + "..." if len(code) > 500 else code
            }
            
            # Save individual result
            result_filename = f"{self.output_dir}/eval_{prompt_info.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_filename, 'w') as f:
                json.dump(evaluation_result, f, indent=2)
            
            print(f"  ✅ Overall Score: {evaluation_result['scores']['overall_score']:.2f}/100")
            
            return evaluation_result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
    
    def _calculate_comprehensive_metrics(self, analysis_results: Dict, prompt_info: Dict) -> DriverEvaluationMetrics:
        """Calculate comprehensive metrics from analysis results"""
        metrics = DriverEvaluationMetrics()
        
        # Compilation metrics
        compilation = analysis_results.get('compilation', {})
        metrics.metrics['compilation']['success_rate'] = 1.0 if compilation.get('success', False) else 0.0
        metrics.metrics['compilation']['warnings_count'] = compilation.get('warnings', 0)
        metrics.metrics['compilation']['errors_count'] = compilation.get('errors', 0)
        
        # Security metrics
        security = analysis_results.get('security', {})
        metrics.metrics['security']['buffer_safety'] = security.get('score', 0) / 100.0
        metrics.metrics['security']['memory_management'] = 1.0 if 'kmalloc' in str(analysis_results) and 'kfree' in str(analysis_results) else 0.0
        metrics.metrics['security']['input_validation'] = 1.0 if security.get('issues_found', 0) == 0 else max(0, 1.0 - security.get('issues_found', 0) * 0.2)
        
        # Code quality metrics
        style = analysis_results.get('style', {})
        metrics.metrics['code_quality']['style_compliance'] = style.get('score', 0) / 100.0
        metrics.metrics['code_quality']['documentation'] = 1.0 if 'MODULE_AUTHOR' in str(analysis_results) else 0.5
        metrics.metrics['code_quality']['maintainability'] = min(1.0, style.get('score', 0) / 100.0)
        
        # Functionality metrics
        functionality = analysis_results.get('functionality', {})
        kernel_patterns = analysis_results.get('kernel_patterns', {})
        
        metrics.metrics['functionality']['basic_operations'] = functionality.get('score', 0) / 100.0
        metrics.metrics['functionality']['error_handling'] = 1.0 if 'return -E' in str(analysis_results) else 0.0
        metrics.metrics['functionality']['kernel_api_usage'] = kernel_patterns.get('score', 0) / 100.0
        
        # Advanced features
        metrics.metrics['advanced_features']['error_recovery'] = 1.0 if functionality.get('elements_found', 0) > 2 else 0.0
        metrics.metrics['advanced_features']['resource_cleanup'] = 1.0 if 'kfree' in str(analysis_results) or 'unregister' in str(analysis_results) else 0.0
        
        return metrics
    
    def _get_category_scores(self, metrics: DriverEvaluationMetrics) -> Dict[str, float]:
        """Get individual category scores"""
        category_scores = {}
        
        for category, data in metrics.metrics.items():
            if isinstance(data, dict) and 'weight' in data:
                scores = [v for k, v in data.items() if k != 'weight' and isinstance(v, (int, float))]
                if scores:
                    category_scores[category] = (sum(scores) / len(scores)) * 100
                else:
                    category_scores[category] = 0.0
        
        return category_scores
    
    def batch_evaluate(self, code_samples: List[Dict], model_name: str = "unknown") -> Dict:
        """Evaluate multiple code samples and generate comprehensive report"""
        
        print(f"\n🚀 Starting batch evaluation for {len(code_samples)} samples")
        print(f"📋 Model: {model_name}")
        print("=" * 60)
        
        results = []
        
        for i, sample in enumerate(code_samples, 1):
            print(f"\n[{i}/{len(code_samples)}] Processing sample...")
            
            try:
                result = self.evaluate_single_code(
                    sample['code'], 
                    sample['prompt_info'], 
                    model_name
                )
                results.append(result)
                
            except Exception as e:
                print(f"  ❌ Error evaluating sample {i}: {str(e)}")
                # Add error result
                error_result = {
                    'metadata': {
                        'prompt_id': sample.get('prompt_info', {}).get('id', 'unknown'),
                        'model_name': model_name,
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e)
                    },
                    'scores': {'overall_score': 0.0},
                    'analysis_details': {'error': str(e)}
                }
                results.append(error_result)
        
        # Generate comprehensive report
        report = self._generate_batch_report(results, model_name)
        
        # Save batch report
        report_filename = f"{self.output_dir}/batch_report_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Batch evaluation completed!")
        print(f"📄 Report saved: {report_filename}")
        
        return report
    
    def _generate_batch_report(self, results: List[Dict], model_name: str) -> Dict:
        """Generate comprehensive batch evaluation report"""
        
        # Calculate summary statistics
        scores = [r['scores']['overall_score'] for r in results if 'overall_score' in r['scores']]
        
        if not scores:
            return {
                'error': 'No valid scores to analyze',
                'model_name': model_name,
                'timestamp': datetime.now().isoformat()
            }
        
        # Category-wise analysis
        category_analysis = {}
        categories = ['compilation', 'functionality', 'security', 'code_quality', 'advanced_features']
        
        for category in categories:
            category_scores = []
            for result in results:
                if 'category_scores' in result['scores'] and category in result['scores']['category_scores']:
                    category_scores.append(result['scores']['category_scores'][category])
            
            if category_scores:
                category_analysis[category] = {
                    'average': sum(category_scores) / len(category_scores),
                    'min': min(category_scores),
                    'max': max(category_scores),
                    'samples': len(category_scores)
                }
        
        report = {
            'summary': {
                'model_name': model_name,
                'total_samples': len(results),
                'successful_evaluations': len(scores),
                'timestamp': datetime.now().isoformat()
            },
            'overall_performance': {
                'average_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores),
                'score_distribution': {
                    'excellent (90-100)': len([s for s in scores if s >= 90]),
                    'good (70-89)': len([s for s in scores if 70 <= s < 90]),
                    'fair (50-69)': len([s for s in scores if 50 <= s < 70]),
                    'poor (0-49)': len([s for s in scores if s < 50])
                }
            },
            'category_analysis': category_analysis,
            'detailed_results': results
        }
        
        return report
