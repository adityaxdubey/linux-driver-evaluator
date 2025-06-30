# src/analyzers/clang_analyzer.py
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
        self.kernel_header_paths = self._get_all_kernel_header_paths(custom_header_path)
        
        # more focused checks that work well in WSL environment
        self.kernel_checks = [
            'bugprone-unused-parameter', 'bugprone-unused-variable',
            'misc-unused-parameters', 'misc-unused-variables',
            'readability-braces-around-statements', 'readability-misleading-indentation',
            'performance-unnecessary-copy-initialization',
            'clang-analyzer-core.NullDereference', 'clang-analyzer-deadcode.DeadStores'
        ]
        
    def _check_clang_availability(self) -> bool:
        try:
            return subprocess.run(['clang-tidy', '--version'], capture_output=True, text=True, timeout=5).returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _get_all_kernel_header_paths(self, custom_base_path: str = None) -> List[str]:
        """get kernel header paths with practical defaults"""
        base_path = custom_base_path
        
        if not base_path:
            try:
                kernel_version = subprocess.check_output(['uname', '-r']).strip().decode()
                base_path = f"/usr/src/linux-headers-{kernel_version}"
            except:
                print("using fallback header paths for WSL environment")
                return ["/usr/include"]  # fallback for WSL

        if not os.path.isdir(base_path):
            print(f"using fallback - base path not found: {base_path}")
            return ["/usr/include"]

        # practical paths that usually exist
        potential_paths = [
            f"{base_path}/include",
            f"{base_path}/arch/x86/include",
            "/usr/include"  # always include standard headers
        ]
        
        found_paths = [path for path in potential_paths if os.path.isdir(path)]
        
        if found_paths:
            print(f"using kernel header paths: {found_paths}")
            return found_paths
        else:
            print("using fallback to standard include path")
            return ["/usr/include"]

    def analyze_code_detailed(self, code: str, filename: str = "driver.c") -> Dict:
        if not self.clang_available:
            return {"error": "clang-tidy not available", "fallback": True}
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, dir='.') as temp_file:
            temp_file.write(code)
            temp_filepath = temp_file.name
        
        try:
            return self._run_detailed_analysis(temp_filepath, code)
        finally:
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
    
    def _run_detailed_analysis(self, filepath: str, original_code: str) -> Dict:
        """run analysis with practical filtering"""
        checks = ','.join(self.kernel_checks)
        file_basename = os.path.basename(filepath)
        
        # THE FIX: add defines to work around missing headers
        include_flags = [f'-I{path}' for path in self.kernel_header_paths]
        defines = [
            '-D__KERNEL__', '-DMODULE',
            '-DREAD_ONCE(x)=(x)',  # define missing macros
            '-DWRITE_ONCE(x,v)=((x)=(v))',
            '-D__user=', '-D__iomem=', '-D__must_check='
        ]
        
        cmd = [
            'clang-tidy', filepath, f'--checks={checks}',
            '--header-filter=^$',  # only analyze our file, not headers
            '--', *include_flags, *defines, '-std=gnu89'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            issues = self._parse_and_filter_output(result.stdout + result.stderr, original_code)
            summary = self._generate_detailed_summary(issues)
            recommendations = self._generate_fix_recommendations(issues)
            
            return {
                "clang_available": True, "analysis_successful": True,
                "issues": [issue.__dict__ for issue in issues],
                "summary": summary, "recommendations": recommendations
            }
        except Exception as e:
            return {"error": f"clang analysis failed: {str(e)}"}
    
    def _parse_and_filter_output(self, output: str, original_code: str) -> List[ClangIssue]:
        """parse output and filter to only issues in our driver code"""
        issues = []
        code_lines = original_code.split('\n')
        max_driver_lines = len(code_lines)
        
        pattern = r'([^:]+):(\d+):(\d+):\s+(warning|error|note):\s+(.+?)\s+\[([^\]]+)\]'
        for match in re.finditer(pattern, output):
            file_path, line_num, col, severity, message, check_name = match.groups()
            
            line_number = int(line_num)
            
            # THE KEY FIX: only include issues from our driver code
            if line_number <= max_driver_lines:
                category = self._categorize_detailed_issue(check_name, message)
                suggestion = self._generate_suggestion(check_name, message)
                issues.append(ClangIssue(
                    severity=severity, type=check_name, line=line_number,
                    column=int(col), message=message.strip(), category=category,
                    file_path=file_path, suggestion=suggestion
                ))
        
        return issues
    
    def _categorize_detailed_issue(self, check_name: str, message: str) -> str:
        check_lower = check_name.lower()
        if 'security' in check_lower: return 'security'
        if 'memory' in check_lower or 'null' in check_lower: return 'memory'
        if 'performance' in check_lower: return 'performance'
        if 'readability' in check_lower: return 'style'
        if 'bugprone' in check_lower or 'unused' in check_lower: return 'reliability'
        return 'general'

    def _generate_suggestion(self, check_name: str, message: str) -> str:
        if 'unused-parameter' in check_name:
            return 'add (void)param_name; to mark as intentionally unused'
        elif 'unused-variable' in check_name:
            return 'remove variable or use it in the code'
        elif 'braces-around-statements' in check_name:
            return 'add braces around if/for/while statement body'
        elif 'null' in check_name.lower():
            return 'add null pointer check before dereference'
        return 'review and fix according to best practices'

    def _generate_detailed_summary(self, issues: List[ClangIssue]) -> Dict:
        by_severity = {'error': 0, 'warning': 0, 'note': 0}
        by_category = {'security': 0, 'memory': 0, 'performance': 0, 'style': 0, 'reliability': 0, 'general': 0}
        critical_issues = []
        
        for issue in issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_category[issue.category] = by_category.get(issue.category, 0) + 1
            if issue.severity == 'error' or issue.category in ['security', 'memory']:
                critical_issues.append(issue)

        # more lenient scoring since we're filtering system issues
        severity_penalty = by_severity['error'] * 15 + by_severity['warning'] * 2
        clang_score = max(0, 100 - severity_penalty)
        
        return {
            'total_issues': len(issues), 'by_severity': by_severity, 'by_category': by_category,
            'critical_issues': len(critical_issues), 'clang_score': round(clang_score, 2),
        }

    def _generate_fix_recommendations(self, issues: List[ClangIssue]) -> List[Dict]:
        if not issues:
            return [{'priority': 'none', 'count': 0, 'description': 'no issues found in driver code'}]
        
        reliability_issues = [i for i in issues if i.category == 'reliability']
        style_issues = [i for i in issues if i.category == 'style']
        
        recommendations = []
        if reliability_issues:
            recommendations.append({
                'priority': 'important', 'count': len(reliability_issues),
                'description': 'fix unused parameters and variables'
            })
        if style_issues:
            recommendations.append({
                'priority': 'style', 'count': len(style_issues),
                'description': 'improve code readability'
            })
        
        return recommendations

class ClangTidyAnalyzer(EnhancedClangAnalyzer):
    def analyze_code(self, code: str, filename: str = "driver.c") -> Dict:
        return self.analyze_code_detailed(code, filename)
