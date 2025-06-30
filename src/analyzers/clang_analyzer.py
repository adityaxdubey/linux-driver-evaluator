import subprocess
import json
import re
import tempfile
import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ClangIssue:
    severity: str
    type: str
    line: int
    column: int
    message: str
    category: str
    file_path: str
    suggestion: str = ""

class EnhancedClangAnalyzer:
    def __init__(self, custom_header_path: str = None):
        self.clang_available = self._check_clang_availability()
        self.kernel_header_path = custom_header_path or self._find_kernel_header_path()
        
        self.kernel_checks = [
            'security-*', 'bugprone-*', 'performance-*', 'readability-*', 'misc-*',
            '-bugprone-easily-swappable-parameters', '-bugprone-magic-numbers',
            '-readability-magic-numbers', '-readability-function-cognitive-complexity',
            'clang-analyzer-*'
        ]
        
    def _check_clang_availability(self) -> bool:
        try:
            return subprocess.run(['clang-tidy', '--version'], capture_output=True, text=True, timeout=5).returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _find_kernel_header_path(self) -> str:
        # THE FIX: More robust auto-detection and clearer error handling
        # 1. Check environment variable first (professional standard)
        env_path = os.getenv('KERNEL_HEADER_PATH')
        if env_path and os.path.isdir(env_path):
            print(f"Using kernel headers from KERNEL_HEADER_PATH: {env_path}")
            return env_path
            
        # 2. Try auto-detection with uname
        try:
            kernel_version = subprocess.check_output(['uname', '-r']).strip().decode()
            
            # Try the non-generic path first
            path1 = f"/usr/src/linux-headers-{kernel_version.replace('-generic', '')}/include"
            if os.path.isdir(path1):
                print(f"Found kernel headers at: {path1}")
                return path1

            # Fallback to the full name path
            path2 = f"/usr/src/linux-headers-{kernel_version}/include"
            if os.path.isdir(path2):
                print(f"Found kernel headers at: {path2}")
                return path2
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # 3. If everything fails, give a clear error message.
        print("\n--- KERNEL HEADER ERROR ---")
        print("Could not automatically find kernel headers.")
        print("Please specify the path using the --kernel-headers flag or KERNEL_HEADER_PATH environment variable.")
        print("Example: --kernel-headers /usr/src/linux-headers-$(uname -r)/include\n")
        return None
    
    def analyze_code_detailed(self, code: str, filename: str = "driver.c") -> Dict:
        if not self.clang_available:
            return {"error": "clang-tidy not available", "fallback": True}
        
        # Check if header path was found
        if not self.kernel_header_path:
            return {"error": "kernel header path not found or specified", "fallback": True}
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, dir='.') as temp_file:
            temp_file.write(code)
            temp_filepath = temp_file.name
        
        try:
            return self._run_detailed_analysis(temp_filepath)
        finally:
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
    
    def _run_detailed_analysis(self, filepath: str) -> Dict:
        checks = ','.join(self.kernel_checks)
        file_basename = os.path.basename(filepath)
        header_filter = f'--header-filter={file_basename}'
        
        cmd = [
            'clang-tidy', filepath, f'--checks={checks}', '--format-style=file',
            header_filter, '--', f'-I{self.kernel_header_path}',
            '-nostdinc', '-D__KERNEL__', '-DMODULE', '-std=gnu89'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            issues = self._parse_detailed_output(result.stdout + result.stderr)
            summary = self._generate_detailed_summary(issues)
            recommendations = self._generate_fix_recommendations(issues)
            
            return {
                "clang_available": True, "analysis_successful": True,
                "issues": [issue.__dict__ for issue in issues],
                "summary": summary, "recommendations": recommendations
            }
        except Exception as e:
            return {"error": f"clang analysis failed: {str(e)}"}
    
    def _parse_detailed_output(self, output: str) -> List[ClangIssue]:
        issues = []
        pattern = r'([^:]+):(\d+):(\d+):\s+(warning|error|note):\s+(.+?)\s+\[([^\]]+)\]'
        for match in re.finditer(pattern, output):
            file_path, line_num, col, severity, message, check_name = match.groups()
            category = self._categorize_detailed_issue(check_name, message)
            suggestion = self._generate_suggestion(check_name, message)
            issues.append(ClangIssue(
                severity=severity, type=check_name, line=int(line_num),
                column=int(col), message=message.strip(), category=category,
                file_path=file_path, suggestion=suggestion
            ))
        return issues
    
    def _categorize_detailed_issue(self, check_name: str, message: str) -> str:
        check_lower = check_name.lower()
        if 'security' in check_lower or 'insecure' in check_lower: return 'security'
        if 'memory' in check_lower or 'null' in check_lower: return 'memory'
        if 'performance' in check_lower: return 'performance'
        if 'readability' in check_lower or 'style' in check_lower: return 'style'
        if 'bugprone' in check_lower: return 'reliability'
        return 'general'

    def _generate_suggestion(self, check_name: str, message: str) -> str:
        suggestions = {
            'bugprone-unused-parameter': 'use (void)param; or __attribute__((unused))',
            'misc-unused-variables': 'remove if not used',
            'clang-analyzer-core.NullDereference': 'add null pointer check',
        }
        for pattern, suggestion in suggestions.items():
            if pattern in check_name: return suggestion
        return 'review code against kernel best practices'

    def _generate_detailed_summary(self, issues: List[ClangIssue]) -> Dict:
        by_severity = {'error': 0, 'warning': 0, 'note': 0}
        by_category = {'security': 0, 'memory': 0, 'performance': 0, 'style': 0, 'reliability': 0, 'general': 0}
        critical_issues = [i for i in issues if i.severity == 'error' or i.category in ['security', 'memory']]
        
        for issue in issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_category[issue.category] = by_category.get(issue.category, 0) + 1

        severity_penalty = by_severity['error'] * 20 + by_severity['warning'] * 3
        clang_score = max(0, 100 - severity_penalty)
        
        return {
            'total_issues': len(issues), 'by_severity': by_severity, 'by_category': by_category,
            'critical_issues': len(critical_issues), 'clang_score': round(clang_score, 2),
        }

    def _generate_fix_recommendations(self, issues: List[ClangIssue]) -> List[Dict]:
        critical = [i for i in issues if i.severity == 'error' or i.category in ['security', 'memory']]
        if critical:
            return [{'priority': 'critical', 'count': len(critical), 'description': 'fix high-priority issues'}]
        return []

class ClangTidyAnalyzer(EnhancedClangAnalyzer):
    def analyze_code(self, code: str, filename: str = "driver.c") -> Dict:
        return self.analyze_code_detailed(code, filename)

