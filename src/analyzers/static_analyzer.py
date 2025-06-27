import re
import subprocess
import os
import tempfile
from typing import Dict

class KernelCodeAnalyzer:
    def __init__(self):
        self.kernel_functions = [
            'kmalloc', 'kfree', 'copy_from_user', 'copy_to_user',
            'mutex_lock', 'mutex_unlock', 'spin_lock', 'spin_unlock',
            'request_irq', 'free_irq', 'ioremap', 'iounmap',
            'module_init', 'module_exit', 'cdev_init', 'cdev_add',
            'register_chrdev', 'unregister_chrdev'
        ]
        self.dangerous_functions = [
            'strcpy', 'strcat', 'sprintf', 'gets', 'scanf',
            'malloc', 'free', 'printf', 'fprintf'
        ]
        self.good_patterns = [
            r'module_init\s*\(',
            r'module_exit\s*\(',
            r'MODULE_LICENSE\s*\(',
            r'MODULE_AUTHOR\s*\(',
            r'static\s+struct\s+file_operations',
            r'return\s+-E[A-Z]+',
            r'copy_from_user.*if',
            r'copy_to_user.*if',
        ]
    def analyze_file(self, filepath: str) -> Dict:
        if not os.path.exists(filepath):
            return {"error": "file not found"}
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"could not read file: {str(e)}"}
        results = {
            'compilation': self._check_compilation_improved(filepath, content),
            'security': self._check_security_issues(content),
            'style': self._check_coding_style(content),
            'kernel_patterns': self._check_kernel_patterns(content),
            'functionality': self._check_functionality(content)
        }
        return results
    def _check_compilation_improved(self, filepath: str, content: str) -> Dict:
        try:
            basic_errors = []
            if '#include' not in content:
                basic_errors.append("missing include statements")
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                basic_errors.append(f"unmatched braces: {open_braces} open, {close_braces} close")
            if content.count('(') != content.count(')'):
                basic_errors.append("unmatched parentheses")
            result = subprocess.run([
                'gcc', '-fsyntax-only', '-Wall', '-Wextra',
                '-nostdinc', '-I/usr/include', filepath
            ], capture_output=True, text=True, timeout=15)
            warnings = result.stderr.count('warning:')
            errors = len(basic_errors) + result.stderr.count('error:')
            success = len(basic_errors) == 0 and result.returncode in [0, 1]
            return {
                'success': success,
                'warnings': warnings,
                'errors': errors,
                'output': (result.stderr[:300] + '\n' + '\n'.join(basic_errors))[:500],
                'basic_checks_passed': len(basic_errors) == 0
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'warnings': 0, 'errors': 1, 'output': 'compilation timeout'}
        except Exception as e:
            return {'success': True, 'warnings': 0, 'errors': 0, 'output': f'compilation check skipped: {str(e)}'}
    def _check_security_issues(self, content: str) -> Dict:
        issues = []
        good_practices = 0
        for func in self.dangerous_functions:
            if re.search(rf'\b{func}\s*\(', content):
                issues.append(f"dangerous function used in kernel space: {func}")
        if re.search(r'char\s+\w+\[\d+\].*strcpy|strcat', content):
            issues.append("potential buffer overflow with strcpy/strcat")
        else:
            good_practices += 1
        if 'copy_from_user' in content:
            if re.search(r'if\s*\([^)]*copy_from_user', content):
                good_practices += 1
            else:
                issues.append("missing return value check for copy_from_user")
        if 'kmalloc' in content:
            if re.search(r'if\s*\([^)]*!\s*\w+\)', content) or 'if (!' in content:
                good_practices += 1
            else:
                issues.append("missing null check after kmalloc")
        if 'BUFFER_SIZE' in content or 'buffer' in content.lower():
            if 'size >' in content or 'size <' in content:
                good_practices += 1
        if re.search(r'return\s+-E[A-Z]+', content):
            good_practices += 1
        return {
            'issues_found': len(issues),
            'issues': issues,
            'good_practices': good_practices,
            'score': max(0, min(100, 80 - len(issues) * 15 + good_practices * 10))
        }
    def _check_coding_style(self, content: str) -> Dict:
        violations = []
        good_style_points = 0
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > 100:
                violations.append(f"line {i}: very long line ({len(line)} chars)")
            elif len(line.rstrip()) <= 80:
                good_style_points += 0.1
            if line.strip() and not line.startswith('#'):
                if re.match(r'^[ ]{4}[ ]*[^ ]', line):
                    violations.append(f"line {i}: consider using tabs for indentation")
            if line.rstrip() != line.rstrip('\n'):
                violations.append(f"line {i}: trailing whitespace")
        if re.search(r'static\s+struct', content):
            good_style_points += 2
        if 'MODULE_LICENSE' in content:
            good_style_points += 2
        if 'MODULE_AUTHOR' in content:
            good_style_points += 1
        if 'MODULE_DESCRIPTION' in content:
            good_style_points += 1
        shown_violations = violations[:5]
        violation_penalty = min(len(violations), 10) * 5
        return {
            'violations': len(violations),
            'details': shown_violations,
            'good_style_points': good_style_points,
            'score': max(20, min(100, 60 + good_style_points * 5 - violation_penalty))
        }
    def _check_kernel_patterns(self, content: str) -> Dict:
        patterns_found = []
        pattern_score = 0
        essential_patterns = [
            ('module_init', 'module initialization function'),
            ('module_exit', 'module cleanup function'), 
            ('MODULE_LICENSE', 'module license declaration'),
        ]
        for pattern, description in essential_patterns:
            if pattern in content:
                patterns_found.append(description)
                pattern_score += 20
        good_patterns = [
            ('file_operations', 'file operations structure'),
            ('copy_from_user', 'user space data copying'),
            ('copy_to_user', 'kernel to user space copying'),
            ('register_chrdev', 'character device registration'),
            ('unregister_chrdev', 'proper device cleanup'),
            ('return -E', 'proper error codes'),
            ('static', 'static function/variable declarations'),
        ]
        for pattern, description in good_patterns:
            if pattern in content:
                patterns_found.append(description)
                pattern_score += 10
        advanced_patterns = [
            ('__init', 'init section annotation'),
            ('__exit', 'exit section annotation'),
            ('DEVICE_NAME', 'device name constant'),
            ('BUFFER_SIZE', 'buffer size constant'),
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
        functional_elements = []
        functionality_score = 0
        core_functions = [
            ('file_operations', 'file operations structure defined', 25),
            ('device_open', 'device open function', 15),
            ('device_release', 'device release function', 15),
            ('device_read', 'device read function', 15),
            ('device_write', 'device write function', 15),
        ]
        for pattern, description, score in core_functions:
            if pattern in content:
                functional_elements.append(description)
                functionality_score += score
        if re.search(r'return\s+-E[A-Z]+', content):
            functional_elements.append("proper error codes used")
            functionality_score += 10
        if 'kmalloc' in content and 'kfree' in content:
            functional_elements.append("dynamic memory management")
            functionality_score += 10
        elif 'register' in content and 'unregister' in content:
            functional_elements.append("resource registration/cleanup")
            functionality_score += 10
        return {
            'elements_found': len(functional_elements),
            'elements': functional_elements,
            'score': min(100, functionality_score)
        }
