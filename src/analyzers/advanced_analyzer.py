# src/analyzers/advanced_analyzer.py
import re
import subprocess
import tempfile
import os
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class SecurityIssue:
    severity: str
    type: str
    line: int
    description: str
    suggestion: str

@dataclass
class PerformanceMetric:
    metric_type: str
    value: float
    unit: str
    impact: str

class KernelASTAnalyzer:
    def __init__(self):
        self.security_issues = []
        self.performance_metrics = []
        self.function_calls = defaultdict(int)
        self.memory_allocations = []
        self.control_flow_complexity = {}
        
    def analyze_ast(self, code: str) -> Dict:
        """comprehensive semantic analysis without full ast parsing"""
        try:
            # reset state
            self.security_issues = []
            self.performance_metrics = []
            self.function_calls = defaultdict(int)
            self.memory_allocations = []
            self.control_flow_complexity = {}
            
            # run semantic analysis
            self._analyze_security_semantic(code)
            self._analyze_performance_semantic(code)
            self._analyze_control_flow_semantic(code)
            self._analyze_memory_management_semantic(code)
            self._analyze_kernel_compliance_semantic(code)
            
            return {
                "security_analysis": self._format_security_results(),
                "performance_analysis": self._format_performance_results(),
                "memory_analysis": self._format_memory_results(),
                "control_flow_analysis": self._format_control_flow_results(),
                "kernel_compliance": self._format_compliance_results(),
                "overall_quality": self._calculate_quality_score()
            }
            
        except Exception as e:
            return {"error": f"semantic analysis failed: {str(e)}"}
    
    def _analyze_security_semantic(self, code: str):
        """advanced security analysis using semantic patterns"""
        lines = code.split('\n')
        
        # buffer overflow detection
        for i, line in enumerate(lines, 1):
            # dangerous string functions
            if re.search(r'\b(strcpy|strcat|sprintf|gets)\s*\(', line):
                self.security_issues.append(SecurityIssue(
                    severity="critical",
                    type="buffer_overflow",
                    line=i,
                    description="unsafe string function usage",
                    suggestion="use strncpy, strncat, snprintf instead"
                ))
            
            # unchecked array access
            if re.search(r'\w+\[[^\]]*\]\s*=', line):
                if not re.search(r'(sizeof|ARRAY_SIZE|<|>)', line):
                    self.security_issues.append(SecurityIssue(
                        severity="medium",
                        type="unchecked_array_access",
                        line=i,
                        description="array access without bounds checking",
                        suggestion="validate array indices"
                    ))
        
        # pointer safety analysis
        self._check_pointer_safety_semantic(code)
        
        # race condition detection
        self._check_concurrency_semantic(code)
        
        # input validation
        self._check_input_validation_semantic(code)
    
    def _check_pointer_safety_semantic(self, code: str):
        """analyze pointer usage patterns"""
        lines = code.split('\n')
        
        # track pointer declarations and usage
        pointer_vars = set()
        null_checked_vars = set()
        
        for i, line in enumerate(lines, 1):
            # find pointer declarations
            ptr_match = re.search(r'(\w+)\s*\*\s*(\w+)', line)
            if ptr_match:
                pointer_vars.add(ptr_match.group(2))
            
            # find null checks
            null_check = re.search(r'if\s*\(\s*!?\s*(\w+)\s*\)', line)
            if null_check:
                null_checked_vars.add(null_check.group(1))
            
            # find pointer dereferences
            deref_match = re.search(r'(\w+)\s*->', line)
            if deref_match:
                var_name = deref_match.group(1)
                if var_name in pointer_vars and var_name not in null_checked_vars:
                    self.security_issues.append(SecurityIssue(
                        severity="high",
                        type="null_pointer_dereference",
                        line=i,
                        description=f"potential null pointer dereference: {var_name}",
                        suggestion="add null pointer check"
                    ))
    
    def _check_concurrency_semantic(self, code: str):
        """analyze concurrency issues"""
        has_locks = bool(re.search(r'\b(mutex_lock|spin_lock|down)\s*\(', code))
        has_unlocks = bool(re.search(r'\b(mutex_unlock|spin_unlock|up)\s*\(', code))
        has_shared_data = bool(re.search(r'\bstatic\s+.*\w+', code))
        
        if has_shared_data and not has_locks:
            self.security_issues.append(SecurityIssue(
                severity="high",
                type="race_condition",
                line=0,
                description="shared data without synchronization",
                suggestion="use locking mechanisms"
            ))
        
        if has_locks and not has_unlocks:
            self.security_issues.append(SecurityIssue(
                severity="critical",
                type="deadlock_risk",
                line=0,
                description="locks acquired but not released",
                suggestion="ensure all locks are properly released"
            ))
    
    def _check_input_validation_semantic(self, code: str):
        """check input validation patterns"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # copy_from_user without validation
            if 'copy_from_user' in line:
                # look for validation in surrounding lines
                context_start = max(0, i-3)
                context_end = min(len(lines), i+3)
                context = '\n'.join(lines[context_start:context_end])
                
                if not re.search(r'if\s*\([^)]*copy_from_user', context):
                    self.security_issues.append(SecurityIssue(
                        severity="high",
                        type="missing_input_validation",
                        line=i,
                        description="copy_from_user without return value check",
                        suggestion="check return value of copy_from_user"
                    ))
    
    def _analyze_performance_semantic(self, code: str):
        """performance analysis using semantic patterns"""
        
        # memory allocation analysis
        alloc_count = len(re.findall(r'\b(kmalloc|kzalloc|vmalloc)\s*\(', code))
        dealloc_count = len(re.findall(r'\b(kfree|vfree)\s*\(', code))
        
        if alloc_count > dealloc_count:
            self.performance_metrics.append(PerformanceMetric(
                metric_type="memory_leak_risk",
                value=alloc_count - dealloc_count,
                unit="allocations",
                impact="high"
            ))
        
        # large allocation detection
        large_allocs = re.findall(r'(kmalloc|kzalloc|vmalloc)\s*\([^)]*[0-9]{4,}[^)]*\)', code)
        if large_allocs:
            self.performance_metrics.append(PerformanceMetric(
                metric_type="large_allocation",
                value=len(large_allocs),
                unit="count",
                impact="medium"
            ))
        
        # io operation analysis
        io_ops = len(re.findall(r'\b(copy_from_user|copy_to_user|ioremap|iounmap)\s*\(', code))
        if io_ops > 5:
            self.performance_metrics.append(PerformanceMetric(
                metric_type="high_io_operations",
                value=io_ops,
                unit="operations",
                impact="medium"
            ))
    
    def _analyze_control_flow_semantic(self, code: str):
        """analyze control flow complexity"""
        lines = code.split('\n')
        current_function = None
        
        for line in lines:
            # function definition
            func_match = re.search(r'^\s*(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*{?', line)
            if func_match and not re.search(r'(if|while|for)', line):
                current_function = func_match.group(1)
                if current_function not in self.control_flow_complexity:
                    self.control_flow_complexity[current_function] = 1
            
            # complexity contributors
            if current_function and re.search(r'\b(if|while|for|switch|case)\b', line):
                self.control_flow_complexity[current_function] += 1
        
        # identify high complexity functions
        for func_name, complexity in self.control_flow_complexity.items():
            if complexity > 10:
                self.performance_metrics.append(PerformanceMetric(
                    metric_type="high_complexity",
                    value=complexity,
                    unit="cyclomatic_complexity",
                    impact="medium"
                ))
    
    def _analyze_memory_management_semantic(self, code: str):
        """detailed memory management analysis"""
        
        # track allocation/deallocation pairs
        alloc_pattern = re.compile(r'(\w+)\s*=\s*(k[mz]?alloc|vmalloc)\s*\(')
        free_pattern = re.compile(r'(kfree|vfree)\s*\(\s*(\w+)\s*\)')
        
        allocated_vars = set()
        freed_vars = set()
        
        for match in alloc_pattern.finditer(code):
            allocated_vars.add(match.group(1))
        
        for match in free_pattern.finditer(code):
            freed_vars.add(match.group(2))
        
        self.memory_allocations = {
            'allocated': allocated_vars,
            'freed': freed_vars,
            'potentially_leaked': allocated_vars - freed_vars
        }
        
        # check for double free
        free_calls = free_pattern.findall(code)
        freed_multiple = [var for var in freed_vars if sum(1 for _, v in free_calls if v == var) > 1]
        
        if freed_multiple:
            self.security_issues.append(SecurityIssue(
                severity="critical",
                type="double_free",
                line=0,
                description=f"potential double free: {', '.join(freed_multiple)}",
                suggestion="ensure variables are freed only once"
            ))
    
    def _analyze_kernel_compliance_semantic(self, code: str):
        """kernel coding standards compliance"""
        self.compliance_score = 0
        
        # proper error codes
        if re.search(r'return\s+-E[A-Z]+', code):
            self.compliance_score += 10
        
        # module structure
        if all(pattern in code for pattern in ['module_init', 'module_exit', 'MODULE_LICENSE']):
            self.compliance_score += 15
        
        # proper cleanup
        if 'module_exit' in code and any(cleanup in code for cleanup in ['kfree', 'unregister', 'free_irq']):
            self.compliance_score += 10
        
        # static declarations
        if re.search(r'\bstatic\s+', code):
            self.compliance_score += 5
        
        # proper includes
        if '#include <linux/' in code:
            self.compliance_score += 5
    
    def _format_security_results(self) -> Dict:
        by_severity = defaultdict(list)
        for issue in self.security_issues:
            by_severity[issue.severity].append(issue.__dict__)
        
        return {
            "total_issues": len(self.security_issues),
            "by_severity": dict(by_severity),
            "risk_score": self._calculate_risk_score()
        }
    
    def _calculate_risk_score(self) -> float:
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        total_risk = sum(weights.get(issue.severity, 1) for issue in self.security_issues)
        return min(100, total_risk * 5)
    
    def _format_performance_results(self) -> Dict:
        return {
            "metrics": [m.__dict__ for m in self.performance_metrics],
            "control_flow_complexity": self.control_flow_complexity,
            "performance_score": self._calculate_performance_score()
        }
    
    def _calculate_performance_score(self) -> float:
        penalty = len([m for m in self.performance_metrics if m.impact in ["high", "critical"]]) * 10
        return max(0, 100 - penalty)
    
    def _format_memory_results(self) -> Dict:
        return {
            "allocations": {k: list(v) if isinstance(v, set) else v 
                          for k, v in self.memory_allocations.items()},
            "memory_score": self._calculate_memory_score()
        }
    
    def _calculate_memory_score(self) -> float:
        if not self.memory_allocations:
            return 85
        
        allocated = len(self.memory_allocations.get('allocated', []))
        freed = len(self.memory_allocations.get('freed', []))
        
        if allocated == 0:
            return 90
        
        balance_ratio = freed / allocated if allocated > 0 else 0
        return min(100, balance_ratio * 100)
    
    def _format_control_flow_results(self) -> Dict:
        if not self.control_flow_complexity:
            return {"function_complexities": {}, "average_complexity": 0, "control_flow_score": 80}
        
        avg_complexity = sum(self.control_flow_complexity.values()) / len(self.control_flow_complexity)
        return {
            "function_complexities": self.control_flow_complexity,
            "average_complexity": avg_complexity,
            "control_flow_score": self._calculate_control_flow_score()
        }
    
    def _calculate_control_flow_score(self) -> float:
        if not self.control_flow_complexity:
            return 80
        
        avg_complexity = sum(self.control_flow_complexity.values()) / len(self.control_flow_complexity)
        return max(0, 100 - (avg_complexity - 5) * 5)
    
    def _format_compliance_results(self) -> Dict:
        return {
            "compliance_score": self.compliance_score,
            "max_compliance_score": 45
        }
    
    def _calculate_quality_score(self) -> float:
        security_weight = 0.3
        performance_weight = 0.25
        memory_weight = 0.25
        compliance_weight = 0.2
        
        security_score = max(0, 100 - self._calculate_risk_score())
        performance_score = self._calculate_performance_score()
        memory_score = self._calculate_memory_score()
        compliance_score = (self.compliance_score / 45) * 100
        
        overall = (
            security_score * security_weight +
            performance_score * performance_weight +
            memory_score * memory_weight +
            compliance_score * compliance_weight
        )
        
        return round(overall, 2)
