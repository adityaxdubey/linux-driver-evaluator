import json
import sys
from datetime import datetime

def generate_simple_report(results_file):
    """Generate a simple text report from evaluation results"""
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    print("Linux Driver Code Evaluation Report")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Summary
    if 'benchmark_summary' in data:
        summary = data['benchmark_summary']
        print("Summary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Average Score: {summary['average_score']:.1f}/100")
        print(f"  Score Range: {summary['min_score']:.1f} - {summary['max_score']:.1f}")
        print()
    
    # Score distribution
    if 'score_distribution' in data:
        dist = data['score_distribution']
        print("Score Distribution:")
        print(f"  Excellent (90+): {dist['excellent_90_plus']}")
        print(f"  Good (70-89): {dist['good_70_89']}")
        print(f"  Fair (50-69): {dist['fair_50_69']}")
        print(f"  Poor (<50): {dist['poor_below_50']}")
        print()
    
    # Individual results
    if 'detailed_results' in data:
        print("Individual Results:")
        for i, result in enumerate(data['detailed_results'][:5], 1):  # Show first 5
            meta = result['metadata']
            score = result['scores']['overall_score']
            print(f"  {i}. {meta['prompt_id']}: {score:.1f}/100")
        print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_report.py <results_file.json>")
        sys.exit(1)
    
    generate_simple_report(sys.argv[1])
