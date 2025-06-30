import os
from typing import Dict, List
import sys
import json
import argparse

sys.path.append('src')
from src.analyzers.clang_analyzer import EnhancedClangAnalyzer

class ClangDetailedReporter:
    def __init__(self, custom_header_path: str = None):
        # Pass the custom path to the analyzer
        self.analyzer = EnhancedClangAnalyzer(custom_header_path)
    
    def analyze_and_report(self, filepath: str, show_all: bool = False):
        if not os.path.exists(filepath):
            print(f"error: file not found - {filepath}")
            return
            
        try:
            with open(filepath, 'r') as f:
                code = f.read()
        except Exception as e:
            print(f"error reading file: {str(e)}")
            return
        
        print(f"running detailed clang analysis on {filepath}...")
        results = self.analyzer.analyze_code_detailed(code, filepath)
        
        if 'error' in results:
            print(f"\nAnalysis Failed: {results['error']}")
            return
        
        self._print_summary(results)
        self._print_critical_issues(results)
        if show_all:
            self._print_all_issues(results['issues'])
    
    def _print_summary(self, results: Dict):
        summary = results['summary']
        print("\n--- Clang Analysis Summary ---")
        print(f"  Score: {summary['clang_score']:.1f}/100")
        print(f"  Total Issues: {summary['total_issues']}")
        print(f"  Critical Issues: {summary['critical_issues']}")
        print("  By Severity:", summary['by_severity'])
        print("  By Category:", summary['by_category'])
    
    def _print_critical_issues(self, results: Dict):
        critical = [i for i in results['issues'] if i['severity'] == 'error' or i['category'] in ['security', 'memory']]
        if critical:
            print("\n--- Critical Issues (Fix First) ---")
            for issue in critical[:10]:
                print(f"  Line {issue['line']}: {issue['severity']} ({issue['category']})")
                print(f"    Message: {issue['message']}")
                print(f"    Fix: {issue['suggestion']}")
    
    def _print_all_issues(self, issues: list):
        if issues:
            print("\n--- All Issues ---")
            for issue in issues[:30]: # Limit to 30 to avoid flooding
                print(f"  Line {issue['line']}: {issue['severity']} ({issue['category']}) - {issue['message']}")

def main():
    parser = argparse.ArgumentParser(description='detailed clang-tidy analysis for linux drivers')
    parser.add_argument('file', help='driver file to analyze')
    parser.add_argument('--all', '-a', action='store_true', help='show all issues')
    # THE FIX: Add a new argument for the kernel header path
    parser.add_argument('--kernel-headers', help='explicit path to kernel headers include directory')
    
    args = parser.parse_args()
    
    # Pass the custom path to the reporter
    reporter = ClangDetailedReporter(args.kernel_headers)
    reporter.analyze_and_report(args.file, args.all)

if __name__ == "__main__":
    main()

