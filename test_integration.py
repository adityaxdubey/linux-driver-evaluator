"""
test the complete integrated system
"""

import sys
import os

sys.path.append('src')
from src.evaluator.master_evaluator import MasterDriverEvaluator

def test_complete_system():
    print("testing integrated evaluation system")
    print("=" * 50)
    
    # create test evaluator
    evaluator = MasterDriverEvaluator()
    
    # test with your existing driver
    if os.path.exists('test_driver.c'):
        with open('test_driver.c', 'r') as f:
            test_code = f.read()
        
        prompt_info = {'id': 'integration_test'}
        
        print("running comprehensive evaluation...")
        results = evaluator.comprehensive_evaluation(test_code, prompt_info)
        
        # print summary
        integrated = results['integrated_scores']
        assessment = results['overall_assessment']
        
        print(f"\nintegration test results:")
        print(f"overall score: {integrated['overall_score']:.1f}/100")
        print(f"grade: {integrated['grade']}")
        print(f"quality level: {assessment['quality_level']}")
        
        print(f"\nmodule scores:")
        for module, score in integrated['individual_scores'].items():
            print(f"  {module}: {score:.1f}")
        
        print(f"\ntest completed successfully!")
        
    else:
        print("test_driver.c not found, create a test file first")

if __name__ == "__main__":
    test_complete_system()
