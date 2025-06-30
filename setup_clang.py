import sys
import subprocess
from src.analyzers.clang_analyzer import ClangInstaller, ClangTidyAnalyzer

def setup_clang():
    print("Linux Driver Evaluator - Clang Setup")
    print("=" * 40)
    
    # check current status
    analyzer = ClangTidyAnalyzer()
    
    if analyzer.clang_available:
        print("clang-tidy is already available")
        
        # test clang-tidy
        test_code = '''
#include <linux/module.h>
int test_function(void) {
    return 0;
}
MODULE_LICENSE("GPL");
'''
        print("\ntesting clang-tidy...")
        result = analyzer.analyze_code(test_code, "test.c")
        
        if result.get('analysis_successful'):
            print("clang-tidy test successful")
            print(f"test found {result.get('summary', {}).get('total_issues', 0)} issues")
        else:
            print("clang-tidy test failed")
            print(f"error: {result.get('error', 'unknown')}")
        
    else:
        print("clang-tidy not found")
        
        # attempt installation
        if ClangInstaller.check_and_install():
            print("clang-tidy setup completed successfully")
        else:
            print("clang-tidy setup failed - system will use fallback analysis")
    
    print("\nsetup complete")

if __name__ == "__main__":
    setup_clang()
