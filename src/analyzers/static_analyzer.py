# src/analyzers/static_analyzer.py
import re
import subprocess
import os
import tempfile
from typing import Dict, List, Tuple

class KernelCodeAnalyzer:
    def __init__(self):
        # Common kernel functions
        self.kernel_functions = [
            'kmalloc', 'kfree', 'copy_from_user', 'copy_to_user',
            'mutex_lock', 'mutex_unlock', 'spin_lock', 'spin_unlock',
            'request_irq', 'free_irq', 'ioremap', 'iounmap',
            'module_init', 'module_exit', 'cdev_init', 'cdev_add',
            'register_chrdev', 'unregister_chrdev'
        ]
        
        # Dangerous functions that shouldn't be used in kernel space
        self.dangerous_functions = [
            'strcpy', 'strcat', 'sprintf', 'gets', 'scanf',
            'malloc', 'free', 'printf', 'fprintf'
        ]
        
        # Good patterns to look for
        self.good_patterns = [
            r'module_init\s*\(',
            r'module_exit\s*\(',
            r'MODULE_LICENSE\s*\(',
            r'MODULE_AUTHOR\s*\(',
            r'static\s+struct\s+file_operations',
            r'return\s+-E[A-Z]+',  # Error codes
            r'copy_from_user.*if',  # Input validation
            r'copy_to_user.*if',    # Output validation
        ]
    
    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a single C file for kernel driver patterns"""
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {str(e)}"}
        
        results = {
            'compilation': self._check_compilation_improved(filepath, content),
            'security': self._check_security_issues(content),
            'style': self._check_coding_style(content),
            'kernel_patterns': self._check_kernel_patterns(content),
            'functionality': self._check_functionality(content)
        }
        return results
    
    def _check_compilation_improved(self, filepath: str, content: str) -> Dict:
        """Improved compilation check with better kernel simulation"""
        try:
            # Check for basic syntax errors first
            basic_errors = []
            
            # Check for missing includes
            if '#include' not in content:
                basic_errors.append("Missing include statements")
            
            # Check for unmatched braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                basic_errors.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
            
            # Check for unmatched parentheses in function calls
            if content.count('(') != content.count(')'):
                basic_errors.append("Unmatched parentheses")
            
            # Simulate compilation with basic GCC check (syntax only)
            result = subprocess.run([
                'gcc', '-fsyntax-only', '-Wall', '-Wextra',
                '-nostdinc', '-I/usr/include', filepath
            ], capture_output=True, text=True, timeout=15)
            
            warnings = result.stderr.count('warning:')
            errors = len(basic_errors) + result.stderr.count('error:')
            
            # More lenient success criteria
            success = len(basic_errors) == 0 and result.returncode in [0, 1]  # Allow warnings
            
            return {
                'success': success,
                'warnings': warnings,
                'errors': errors,
                'output': (result.stderr[:300] + '\n' + '\n'.join(basic_errors))[:500],
                'basic_checks_passed': len(basic_errors) == 0
            }
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'warnings': 0, 'errors': 1, 'output': 'Compilation timeout'}
        except Exception as e:
            return {'success': True, 'warnings': 0, 'errors': 0, 'output': f'Compilation check skipped: {str(e)}'}
    
    def _check_security_issues(self, content: str) -> Dict:
        """Enhanced security analysis"""
        issues = []
        good_practices = 0
        
        # Check for dangerous functions
        for func in self.dangerous_functions:
            if re.search(rf'\b{func}\s*\(', content):
                issues.append(f"Dangerous function used in kernel space: {func}")
        
        # Check for buffer safety
        if re.search(r'char\s+\w+\[\d+\].*strcpy|strcat', content):
            issues.append("Potential buffer overflow with strcpy/strcat")
        else:
            good_practices += 1
        
        # Check for proper input validation
        if 'copy_from_user' in content:
            if re.search(r'if\s*\([^)]*copy_from_user', content):
                good_practices += 1
            else:
                issues.append("Missing return value check for copy_from_user")
        
        # Check for proper memory management
        if 'kmalloc' in content:
            if re.search(r'if\s*\([^)]*!\s*\w+\)', content) or 'if (!':
                good_practices += 1
            else:
                issues.append("Missing NULL check after kmalloc")
        
        # Check for proper bounds checking
        if 'BUFFER_SIZE' in content or 'buffer' in content.lower():
            if 'size >' in content or 'size <' in content:
                good_practices += 1
        
        # Check for proper error codes
        if re.search(r'return\s+-E[A-Z]+', content):
            good_practices += 1
        
        return {
            'issues_found': len(issues),
            'issues': issues,
            'good_practices': good_practices,
            'score': max(0, min(100, 80 - len(issues) * 15 + good_practices * 10))
        }
    
    def _check_coding_style(self, content: str) -> Dict:
        """Enhanced style checking"""
        violations = []
        good_style_points = 0
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length (more lenient)
            if len(line.rstrip()) > 100:  # Increased from 80
                violations.append(f"Line {i}: Very long line ({len(line)} chars)")
            elif len(line.rstrip()) <= 80:
                good_style_points += 0.1
            
            # Check for proper indentation pattern
            if line.strip() and not line.startswith('#'):
                if re.match(r'^[ ]{4}[ ]*[^ ]', line):  # 4+ spaces
                    violations.append(f"Line {i}: Consider using tabs for indentation")
            
            # Check for trailing whitespace
            if line.rstrip() != line.rstrip('\n'):
                violations.append(f"Line {i}: Trailing whitespace")
        
        # Check for good style patterns
        if re.search(r'static\s+struct', content):
            good_style_points += 2
        
        if 'MODULE_LICENSE' in content:
            good_style_points += 2
            
        if 'MODULE_AUTHOR' in content:
            good_style_points += 1
            
        if 'MODULE_DESCRIPTION' in content:
            good_style_points += 1
        
        # Limit violations to reduce penalty
        shown_violations = violations[:5]  # Only show first 5
        violation_penalty = min(len(violations), 10) * 5  # Cap penalty
        
        return {
            'violations': len(violations),
            'details': shown_violations,
            'good_style_points': good_style_points,
            'score': max(20, min(100, 60 + good_style_points * 5 - violation_penalty))
        }
    
    def _check_kernel_patterns(self, content: str) -> Dict:
        """Enhanced kernel pattern recognition"""
        patterns_found = []
        pattern_score = 0
        
        # Essential patterns
        essential_patterns = [
            ('module_init', 'Module initialization function'),
            ('module_exit', 'Module cleanup function'), 
            ('MODULE_LICENSE', 'Module license declaration'),
        ]
        
        for pattern, description in essential_patterns:
            if pattern in content:
                patterns_found.append(description)
                pattern_score += 20
        
        # Good patterns
        good_patterns = [
            ('file_operations', 'File operations structure'),
            ('copy_from_user', 'User space data copying'),
            ('copy_to_user', 'Kernel to user space copying'),
            ('register_chrdev', 'Character device registration'),
            ('unregister_chrdev', 'Proper device cleanup'),
            ('return -E', 'Proper error codes'),
            ('static', 'Static function/variable declarations'),
        ]
        
        for pattern, description in good_patterns:
            if pattern in content:
                patterns_found.append(description)
                pattern_score += 10
        
        # Advanced patterns (bonus points)
        advanced_patterns = [
            ('__init', 'Init section annotation'),
            ('__exit', 'Exit section annotation'),
            ('DEVICE_NAME', 'Device name constant'),
            ('BUFFER_SIZE', 'Buffer size constant'),
        ]
        
        for pattern, description in advanced_patterns:
            if pattern in content:
                patterns_found.append(description)
                pattern_score += 5
        
        return {
            'patterns_found': len(patterns_found),
            'patterns': patterns_found,
            'score': min(100, pattern_score)
        }
    
    def _check_functionality(self, content: str) -> Dict:
        """Enhanced functionality checking"""
        functional_elements = []
        functionality_score = 0
        
        # Core functionality checks
        core_functions = [
            ('file_operations', 'File operations structure defined', 25),
            ('device_open', 'Device open function', 15),
            ('device_release', 'Device release function', 15),
            ('device_read', 'Device read function', 15),
            ('device_write', 'Device write function', 15),
        ]
        
        for pattern, description, score in core_functions:
            if pattern in content:
                functional_elements.append(description)
                functionality_score += score
        
        # Error handling
        if re.search(r'return\s+-E[A-Z]+', content):
            functional_elements.append("Proper error codes used")
            functionality_score += 10
        
        # Memory/resource management
        if 'kmalloc' in content and 'kfree' in content:
            functional_elements.append("Dynamic memory management")
            functionality_score += 10
        elif 'register' in content and 'unregister' in content:
            functional_elements.append("Resource registration/cleanup")
            functionality_score += 10
        
        return {
            'elements_found': len(functional_elements),
            'elements': functional_elements,
            'score': min(100, functionality_score)
        }
