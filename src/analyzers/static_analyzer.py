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
            'module_init', 'module_exit', 'cdev_init', 'cdev_add'
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
            'compilation': self._check_compilation(filepath),
            'security': self._check_security_issues(content),
            'style': self._check_coding_style(content),
            'kernel_patterns': self._check_kernel_patterns(content),
            'functionality': self._check_functionality(content)
        }
        return results
    
    def _check_compilation(self, filepath: str) -> Dict:
        """Check if code compiles (basic syntax check)"""
        try:
            # Simple compilation check with basic kernel headers
            result = subprocess.run([
                'gcc', '-c', '-Wall', '-Wextra', '-fsyntax-only',
                '-nostdinc', '-I/usr/include', filepath
            ], capture_output=True, text=True, timeout=30)
            
            warnings = result.stderr.count('warning:')
            errors = result.stderr.count('error:')
            
            return {
                'success': result.returncode == 0 and errors == 0,
                'warnings': warnings,
                'errors': errors,
                'output': result.stderr[:500]  # Truncate output
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'warnings': 0, 'errors': 1, 'output': 'Compilation timeout'}
        except Exception as e:
            return {'success': False, 'warnings': 0, 'errors': 1, 'output': str(e)}
    
    def _check_security_issues(self, content: str) -> Dict:
        """Check for common security issues"""
        issues = []
        
        # Check for dangerous functions
        for func in self.dangerous_functions:
            if re.search(rf'\b{func}\s*\(', content):
                issues.append(f"Dangerous function used in kernel space: {func}")
        
        # Check for potential buffer overflows
        if re.search(r'char\s+\w+\[\d+\].*strcpy|strcat', content):
            issues.append("Potential buffer overflow with strcpy/strcat")
        
        # Check for missing input validation
        if 'copy_from_user' in content:
            if not re.search(r'if\s*\([^)]*copy_from_user', content):
                issues.append("Missing return value check for copy_from_user")
        
        # Check for proper error handling
        if 'kmalloc' in content and 'if' not in content:
            issues.append("Missing NULL check after kmalloc")
        
        return {
            'issues_found': len(issues),
            'issues': issues,
            'score': max(0, 100 - len(issues) * 15)
        }
    
    def _check_coding_style(self, content: str) -> Dict:
        """Check kernel coding style compliance"""
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length (kernel prefers 80 chars)
            if len(line.rstrip()) > 80:
                violations.append(f"Line {i}: Line too long ({len(line)} chars)")
            
            # Check for spaces instead of tabs for indentation
            if re.match(r'^    ', line) and not line.strip().startswith('*'):
                violations.append(f"Line {i}: Use tabs instead of spaces for indentation")
            
            # Check for trailing whitespace
            if line.rstrip() != line.rstrip('\n'):
                violations.append(f"Line {i}: Trailing whitespace")
        
        return {
            'violations': len(violations),
            'details': violations[:10],  # Limit to first 10
            'score': max(0, 100 - len(violations) * 2)
        }
    
    def _check_kernel_patterns(self, content: str) -> Dict:
        """Check for proper kernel programming patterns"""
        patterns_found = []
        
        # Check for good patterns
        for pattern in self.good_patterns:
            if re.search(pattern, content):
                patterns_found.append(f"Found pattern: {pattern}")
        
        # Check for proper module structure
        has_init = 'module_init' in content
        has_exit = 'module_exit' in content
        has_license = 'MODULE_LICENSE' in content
        
        if has_init and has_exit:
            patterns_found.append("Proper module init/exit structure")
        
        if has_license:
            patterns_found.append("Module license specified")
        
        return {
            'patterns_found': len(patterns_found),
            'patterns': patterns_found,
            'score': min(100, len(patterns_found) * 20)
        }
    
    def _check_functionality(self, content: str) -> Dict:
        """Check for functional completeness"""
        functional_elements = []
        
        # Check for file operations
        if 'file_operations' in content:
            functional_elements.append("File operations structure defined")
        
        # Check for device registration
        if any(func in content for func in ['cdev_add', 'register_chrdev', 'platform_driver_register']):
            functional_elements.append("Device registration present")
        
        # Check for error handling
        if re.search(r'return\s+-E[A-Z]+', content):
            functional_elements.append("Proper error codes used")
        
        # Check for memory management
        if 'kmalloc' in content and 'kfree' in content:
            functional_elements.append("Memory management present")
        
        return {
            'elements_found': len(functional_elements),
            'elements': functional_elements,
            'score': min(100, len(functional_elements) * 25)
        }
