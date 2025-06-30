import ast
import re
import subprocess
import tempfile
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

@dataclass
class CodeIssue:
    category: str
    severity: str
    line: int
    column: int
    message: str
    suggestion: str
    confidence: float

class AdvancedStaticAnalyzer:
    def __init__(self):
        self.issues = []
        self.metrics = {}
        self.dependency_graph = {}
        
    def deep_static_analysis(self, code: str) -> Dict:
        """comprehensive static analysis using multiple techniques"""
        
        results = {
            'syntax_analysis': self._analyze_syntax_patterns(code),
            'semantic_analysis': self._analyze_semantic_patterns(code),
            'control_flow_analysis': self._analyze_control_flow(code),
            'data_flow_analysis': self._analyze_data_flow(code),
            'dependency_analysis': self._analyze_dependencies(code),
            'complexity_metrics': self._calculate_complexity_metrics(code),
            'kernel_specific_analysis': self._analyze_kernel_patterns(code)
        }
        
        # calculate comprehensive static score
        results['static_analysis_score'] = self._calculate_static_score(results)
        return results
    
    def _analyze_syntax_patterns(self, code: str) -> Dict:
        """deep syntax pattern analysis"""
        patterns = {
            'function_definitions': [],
            'variable_declarations': [],
            'struct_definitions': [],
            'macro_usage': [],
            'include_dependencies': []
        }
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # function definitions
            func_match = re.search(r'^\s*(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*{?', line)
            if func_match and not re.search(r'(if|while|for)', line):
                patterns['function_definitions'].append({
                    'name': func_match.group(1),
                    'line': i,
                    'signature': line.strip()
                })
            
            # variable declarations
            var_match = re.search(r'^\s*(?:static\s+)?(?:const\s+)?(\w+)\s+(\w+)', line)
            if var_match and not re.search(r'(return|if|while)', line):
                patterns['variable_declarations'].append({
                    'type': var_match.group(1),
                    'name': var_match.group(2),
                    'line': i
                })
        
        return patterns
    
    def _analyze_semantic_patterns(self, code: str) -> Dict:
        """semantic analysis for meaning and intent"""
        semantic_issues = []
        
        # analyze function call patterns
        function_calls = re.findall(r'(\w+)\s*\([^)]*\)', code)
        call_frequency = {}
        for call in function_calls:
            call_frequency[call] = call_frequency.get(call, 0) + 1
        
        # detect potential issues
        if 'kmalloc' in call_frequency and call_frequency.get('kfree', 0) == 0:
            semantic_issues.append({
                'type': 'memory_leak_pattern',
                'severity': 'high',
                'description': 'kmalloc called without corresponding kfree'
            })
        
        # analyze error handling patterns
        error_returns = len(re.findall(r'return\s+-E[A-Z]+', code))
        total_returns = len(re.findall(r'return\s+', code))
        
        error_handling_ratio = error_returns / max(1, total_returns)
        
        return {
            'function_call_frequency': call_frequency,
            'semantic_issues': semantic_issues,
            'error_handling_ratio': error_handling_ratio,
            'semantic_score': self._calculate_semantic_score(semantic_issues, error_handling_ratio)
        }
    
    def _analyze_control_flow(self, code: str) -> Dict:
        """control flow analysis for complexity and paths"""
        
        # detect control structures
        control_structures = {
            'if_statements': len(re.findall(r'\bif\s*\(', code)),
            'for_loops': len(re.findall(r'\bfor\s*\(', code)),
            'while_loops': len(re.findall(r'\bwhile\s*\(', code)),
            'switch_statements': len(re.findall(r'\bswitch\s*\(', code)),
            'goto_statements': len(re.findall(r'\bgoto\s+\w+', code))
        }
        
        # calculate cyclomatic complexity
        complexity = 1 + sum(control_structures.values())
        
        # analyze nesting depth
        max_nesting = self._calculate_max_nesting_depth(code)
        
        return {
            'control_structures': control_structures,
            'cyclomatic_complexity': complexity,
            'max_nesting_depth': max_nesting,
            'control_flow_score': self._calculate_control_flow_score(complexity, max_nesting)
        }
    
    def _analyze_data_flow(self, code: str) -> Dict:
        """data flow analysis for variable usage patterns"""
        
        # track variable definitions and usages
        variable_definitions = {}
        variable_usages = {}
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # find variable definitions
            var_def = re.search(r'(\w+)\s*=\s*', line)
            if var_def:
                var_name = var_def.group(1)
                if var_name not in variable_definitions:
                    variable_definitions[var_name] = []
                variable_definitions[var_name].append(i)
            
            # find variable usages
            for var in variable_definitions:
                if var in line and f'{var}=' not in line:
                    if var not in variable_usages:
                        variable_usages[var] = []
                    variable_usages[var].append(i)
        
        # identify unused variables
        unused_variables = [var for var in variable_definitions if var not in variable_usages]
        
        return {
            'variable_definitions': variable_definitions,
            'variable_usages': variable_usages,
            'unused_variables': unused_variables,
            'data_flow_score': self._calculate_data_flow_score(unused_variables)
        }
    
    def _analyze_dependencies(self, code: str) -> Dict:
        """analyze code dependencies and coupling"""
        
        includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', code)
        
        # categorize includes
        kernel_includes = [inc for inc in includes if inc.startswith('linux/')]
        system_includes = [inc for inc in includes if not inc.startswith('linux/')]
        
        # analyze function dependencies
        function_calls = re.findall(r'(\w+)\s*\(', code)
        external_calls = [call for call in function_calls if call in ['kmalloc', 'printk', 'copy_from_user']]
        
        return {
            'total_includes': len(includes),
            'kernel_includes': kernel_includes,
            'system_includes': system_includes,
            'external_function_calls': external_calls,
            'dependency_score': self._calculate_dependency_score(includes, external_calls)
        }
    
    def _calculate_complexity_metrics(self, code: str) -> Dict:
        """calculate various complexity metrics"""
        
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        metrics = {
            'lines_of_code': len(non_empty_lines),
            'comment_lines': len([line for line in lines if line.strip().startswith('//')]),
            'function_count': len(re.findall(r'^\s*(?:static\s+)?\w+\s+\w+\s*\([^)]*\)\s*{', code, re.MULTILINE)),
            'average_function_length': 0,
            'comment_ratio': 0
        }
        
        if metrics['function_count'] > 0:
            metrics['average_function_length'] = metrics['lines_of_code'] / metrics['function_count']
        
        if len(lines) > 0:
            metrics['comment_ratio'] = metrics['comment_lines'] / len(lines)
        
        return metrics
    
    def _analyze_kernel_patterns(self, code: str) -> Dict:
        """kernel-specific pattern analysis"""
        
        kernel_patterns = {
            'module_structure': {
                'has_init': 'module_init' in code,
                'has_exit': 'module_exit' in code,
                'has_license': 'MODULE_LICENSE' in code,
                'has_author': 'MODULE_AUTHOR' in code
            },
            'device_driver_patterns': {
                'file_operations': 'file_operations' in code,
                'device_open': 'device_open' in code or '.open' in code,
                'device_release': 'device_release' in code or '.release' in code,
                'device_read': 'device_read' in code or '.read' in code,
                'device_write': 'device_write' in code or '.write' in code
            },
            'memory_patterns': {
                'uses_kmalloc': 'kmalloc' in code,
                'uses_kfree': 'kfree' in code,
                'uses_copy_from_user': 'copy_from_user' in code,
                'uses_copy_to_user': 'copy_to_user' in code
            }
        }
        
        # calculate pattern completeness scores
        module_score = sum(kernel_patterns['module_structure'].values()) / len(kernel_patterns['module_structure']) * 100
        driver_score = sum(kernel_patterns['device_driver_patterns'].values()) / len(kernel_patterns['device_driver_patterns']) * 100
        memory_score = sum(kernel_patterns['memory_patterns'].values()) / len(kernel_patterns['memory_patterns']) * 100
        
        return {
            'patterns': kernel_patterns,
            'pattern_scores': {
                'module_structure_score': module_score,
                'driver_patterns_score': driver_score,
                'memory_patterns_score': memory_score
            },
            'overall_kernel_score': (module_score + driver_score + memory_score) / 3
        }
    
    def _calculate_max_nesting_depth(self, code: str) -> int:
        """calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _calculate_static_score(self, results: Dict) -> float:
        """calculate overall static analysis score"""
        
        weights = {
            'semantic': 0.25,
            'control_flow': 0.20,
            'data_flow': 0.15,
            'dependency': 0.15,
            'kernel_specific': 0.25
        }
        
        semantic_score = results['semantic_analysis']['semantic_score']
        control_score = results['control_flow_analysis']['control_flow_score']
        data_score = results['data_flow_analysis']['data_flow_score']
        dependency_score = results['dependency_analysis']['dependency_score']
        kernel_score = results['kernel_specific_analysis']['overall_kernel_score']
        
        overall_score = (
            semantic_score * weights['semantic'] +
            control_score * weights['control_flow'] +
            data_score * weights['data_flow'] +
            dependency_score * weights['dependency'] +
            kernel_score * weights['kernel_specific']
        )
        
        return round(overall_score, 2)
    
    def _calculate_semantic_score(self, issues: List, error_ratio: float) -> float:
        severity_penalties = {'high': 20, 'medium': 10, 'low': 5}
        penalty = sum(severity_penalties.get(issue['severity'], 5) for issue in issues)
        error_bonus = min(20, error_ratio * 100)
        return max(0, 100 - penalty + error_bonus)
    
    def _calculate_control_flow_score(self, complexity: int, nesting: int) -> float:
        complexity_penalty = max(0, (complexity - 10) * 3)
        nesting_penalty = max(0, (nesting - 4) * 5)
        return max(0, 100 - complexity_penalty - nesting_penalty)
    
    def _calculate_data_flow_score(self, unused_vars: List) -> float:
        penalty = len(unused_vars) * 10
        return max(0, 100 - penalty)
    
    def _calculate_dependency_score(self, includes: List, external_calls: List) -> float:
        include_penalty = max(0, (len(includes) - 10) * 2)
        external_penalty = max(0, (len(external_calls) - 20) * 1)
        return max(0, 100 - include_penalty - external_penalty)
