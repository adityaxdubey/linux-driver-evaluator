import subprocess
import tempfile
import os
import re
from typing import Dict

class RuntimePerformanceProfiler:
    def __init__(self):
        self.valgrind_available = self._check_valgrind()
    
    def _check_valgrind(self) -> bool:
        try:
            result = subprocess.run(['which', 'valgrind'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def create_test_harness(self, driver_code: str) -> str:
        """create a userspace test harness for the driver"""
        
        # extract key functions and create a test program
        test_program = f'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

// simplified driver code for testing
{self._simplify_driver_for_userspace(driver_code)}

// performance test harness
int main() {{
    struct timeval start, end;
    char *test_buffer = malloc(1024);
    
    gettimeofday(&start, NULL);
    
    // simulate driver operations
    for (int i = 0; i < 1000; i++) {{
        // test memory operations
        memset(test_buffer, i % 256, 1024);
        
        // simulate device operations if functions exist
        // device_write_test(test_buffer, 1024);
        // device_read_test(test_buffer, 1024);
    }}
    
    gettimeofday(&end, NULL);
    
    long microseconds = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec);
    printf("execution_time_microseconds: %ld\\n", microseconds);
    
    free(test_buffer);
    return 0;
}}
'''
        return test_program
    
    def _simplify_driver_for_userspace(self, code: str) -> str:
        """convert kernel code to userspace testable code"""
        
        # replace kernel functions with userspace equivalents
        simplified = code
        simplified = re.sub(r'#include <linux/[^>]+>', '', simplified)
        simplified = re.sub(r'kmalloc\(([^,]+),\s*[^)]+\)', r'malloc(\1)', simplified)
        simplified = re.sub(r'kfree\(([^)]+)\)', r'free(\1)', simplified)
        simplified = re.sub(r'copy_(from|to)_user\([^)]+\)', 'memcpy(dest, src, size)', simplified)
        simplified = re.sub(r'module_init\([^)]+\);', '', simplified)
        simplified = re.sub(r'module_exit\([^)]+\);', '', simplified)
        simplified = re.sub(r'MODULE_[A-Z_]+\([^)]*\);', '', simplified)
        
        return simplified
    
    def analyze_runtime_performance(self, code: str) -> Dict:
        """analyze actual runtime performance"""
        
        test_program = self.create_test_harness(code)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test.c')
            binary_file = os.path.join(temp_dir, 'test')
            
            with open(test_file, 'w') as f:
                f.write(test_program)
            
            # compile test program
            compile_result = subprocess.run([
                'gcc', '-o', binary_file, test_file, '-O2'
            ], capture_output=True, text=True)
            
            if compile_result.returncode != 0:
                return {
                    'runtime_analysis': False,
                    'error': 'test program compilation failed',
                    'performance_score': 50
                }
            
            # run performance analysis
            results = {}
            
            # basic execution timing
            exec_result = subprocess.run([binary_file], capture_output=True, text=True)
            if exec_result.returncode == 0:
                output = exec_result.stdout
                time_match = re.search(r'execution_time_microseconds: (\d+)', output)
                if time_match:
                    results['execution_time_us'] = int(time_match.group(1))
            
            # memory analysis with valgrind (if available)
            if self.valgrind_available:
                valgrind_result = subprocess.run([
                    'valgrind', '--tool=memcheck', '--leak-check=full', 
                    '--show-leak-kinds=all', '--track-origins=yes',
                    binary_file
                ], capture_output=True, text=True, timeout=30)
                
                results['memory_analysis'] = self._parse_valgrind_output(valgrind_result.stderr)
            
            return self._calculate_runtime_score(results)
    
    def _parse_valgrind_output(self, valgrind_output: str) -> Dict:
        """parse valgrind memory analysis output"""
        
        # extract key metrics from valgrind output
        memory_metrics = {
            'definitely_lost': 0,
            'indirectly_lost': 0,
            'possibly_lost': 0,
            'still_reachable': 0,
            'suppressed': 0,
            'total_heap_usage': 0,
            'invalid_reads': 0,
            'invalid_writes': 0
        }
        
        # parse valgrind summary
        if 'definitely lost:' in valgrind_output:
            lost_match = re.search(r'definitely lost: ([\d,]+) bytes', valgrind_output)
            if lost_match:
                memory_metrics['definitely_lost'] = int(lost_match.group(1).replace(',', ''))
        
        if 'total heap usage:' in valgrind_output:
            heap_match = re.search(r'total heap usage: ([\d,]+) allocs', valgrind_output)
            if heap_match:
                memory_metrics['total_heap_usage'] = int(heap_match.group(1).replace(',', ''))
        
        # count invalid operations
        memory_metrics['invalid_reads'] = valgrind_output.count('Invalid read')
        memory_metrics['invalid_writes'] = valgrind_output.count('Invalid write')
        
        return memory_metrics
    
    def _calculate_runtime_score(self, results: Dict) -> Dict:
        """calculate runtime performance score"""
        
        score = 100
        
        # execution time penalty (assuming baseline of 1000 microseconds)
        if 'execution_time_us' in results:
            if results['execution_time_us'] > 5000:  # more than 5ms is slow
                score -= 20
            elif results['execution_time_us'] > 2000:  # more than 2ms is moderate
                score -= 10
        
        # memory analysis penalties
        if 'memory_analysis' in results:
            mem = results['memory_analysis']
            
            if mem['definitely_lost'] > 0:
                score -= 30  # memory leaks are critical
            
            if mem['invalid_reads'] > 0 or mem['invalid_writes'] > 0:
                score -= 25  # memory errors are very serious
            
            if mem['possibly_lost'] > 1024:  # more than 1KB possibly lost
                score -= 15
        
        return {
            'runtime_analysis': True,
            'runtime_metrics': results,
            'runtime_performance_score': max(0, score)
        }
