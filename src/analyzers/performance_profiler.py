import re
from typing import Dict, List

class PerformanceProfiler:
    def __init__(self):
        self.hotspots = []
        self.complexity_metrics = {}
    
    def analyze_performance_patterns(self, code: str) -> Dict:
        """advanced performance analysis"""
        
        metrics = {
            'algorithmic_complexity': self._analyze_algorithmic_complexity(code),
            'memory_patterns': self._analyze_memory_patterns(code),
            'io_patterns': self._analyze_io_patterns(code),
            'locking_analysis': self._analyze_locking_patterns(code),
            'performance_score': 0
        }
        
        # calculate performance score
        complexity_penalty = metrics['algorithmic_complexity']['max_complexity'] * 5
        memory_penalty = metrics['memory_patterns']['risk_factors'] * 10
        io_penalty = metrics['io_patterns']['blocking_operations'] * 3
        
        metrics['performance_score'] = max(0, 100 - complexity_penalty - memory_penalty - io_penalty)
        
        return metrics
    
    def _analyze_algorithmic_complexity(self, code: str) -> Dict:
        """detect nested loops and complex algorithms"""
        lines = code.split('\n')
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            if re.search(r'\b(for|while)\s*\(', line):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif '}' in line:
                current_nesting = max(0, current_nesting - 1)
        
        return {
            'max_nesting_level': max_nesting,
            'max_complexity': min(10, max_nesting * 2),
            'complex_functions': self._find_complex_functions(code)
        }
    
    def _analyze_memory_patterns(self, code: str) -> Dict:
        """analyze memory allocation patterns"""
        allocations = len(re.findall(r'\b(kmalloc|kzalloc|vmalloc)\b', code))
        deallocations = len(re.findall(r'\b(kfree|vfree)\b', code))
        large_allocations = len(re.findall(r'(kmalloc|kzalloc)\s*\([^)]*[0-9]{4,}', code))
        
        return {
            'total_allocations': allocations,
            'total_deallocations': deallocations,
            'large_allocations': large_allocations,
            'risk_factors': max(0, allocations - deallocations) + large_allocations
        }
    
    def _analyze_io_patterns(self, code: str) -> Dict:
        """analyze I/O operation patterns"""
        blocking_ops = len(re.findall(r'\b(copy_from_user|copy_to_user|msleep|wait_event)\b', code))
        dma_ops = len(re.findall(r'\b(dma_alloc|dma_map)\b', code))
        
        return {
            'blocking_operations': blocking_ops,
            'dma_operations': dma_ops,
            'io_complexity': blocking_ops + dma_ops * 2
        }
    
    def _analyze_locking_patterns(self, code: str) -> Dict:
        """analyze locking and synchronization"""
        locks = re.findall(r'\b(mutex_lock|spin_lock|down)\b', code)
        unlocks = re.findall(r'\b(mutex_unlock|spin_unlock|up)\b', code)
        
        return {
            'lock_operations': len(locks),
            'unlock_operations': len(unlocks),
            'potential_deadlocks': max(0, len(locks) - len(unlocks))
        }
    
    def _find_complex_functions(self, code: str) -> List[str]:
        """identify functions with high complexity"""
        complex_funcs = []
        lines = code.split('\n')
        current_func = None
        complexity = 0
        
        for line in lines:
            func_match = re.search(r'^\s*(?:static\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*{?', line)
            if func_match:
                if current_func and complexity > 5:
                    complex_funcs.append(f"{current_func} (complexity: {complexity})")
                current_func = func_match.group(1)
                complexity = 1
            elif current_func and re.search(r'\b(if|while|for|switch)\b', line):
                complexity += 1
        
        return complex_funcs
