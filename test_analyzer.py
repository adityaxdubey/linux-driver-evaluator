import sys
import os
sys.path.append('src')

from analyzers.static_analyzer import KernelCodeAnalyzer
from metrics.evaluation_metrics import DriverEvaluationMetrics
from tests.test_cases.sample_prompts import SAMPLE_CODES

def test_analyzer():
    print("Testing Linux Driver Code Analyzer")
    print("=" * 50)
    
    analyzer = KernelCodeAnalyzer()
    
    # Test with good driver code
    print("\n1. Testing GOOD driver code:")
    
    # Save good code to temp file
    with open('temp_good_driver.c', 'w') as f:
        f.write(SAMPLE_CODES['good_basic_driver'])
    
    results = analyzer.analyze_file('temp_good_driver.c')
    print(f"Compilation: {results['compilation']['success']}")
    print(f"Security Issues: {results['security']['issues_found']}")
    print(f"Style Score: {results['style']['score']}")
    print(f"Kernel Patterns: {results['kernel_patterns']['patterns_found']}")
    
    # Test with bad driver code
    print("\n2. Testing BAD driver code:")
    
    # Save bad code to temp file
    with open('temp_bad_driver.c', 'w') as f:
        f.write(SAMPLE_CODES['bad_basic_driver'])
    
    results = analyzer.analyze_file('temp_bad_driver.c')
    print(f"Compilation: {results['compilation']['success']}")
    print(f"Security Issues: {results['security']['issues_found']}")
    print(f"Security Issues List: {results['security']['issues']}")
    
    # Test metrics calculation
    print("\n3. Testing Metrics Calculation:")
    metrics = DriverEvaluationMetrics()
    
    # Simulate some scores
    metrics.metrics['compilation']['success_rate'] = 1.0
    metrics.metrics['security']['buffer_safety'] = 0.8
    metrics.metrics['code_quality']['style_compliance'] = 0.9
    
    overall_score = metrics.calculate_overall_score()
    print(f"Overall Score: {overall_score:.2f}")
    
    # Clean up temp files
    os.remove('temp_good_driver.c')
    os.remove('temp_bad_driver.c')
    
    print("\nBasic testing completed!")

if __name__ == "__main__":
    test_analyzer()
