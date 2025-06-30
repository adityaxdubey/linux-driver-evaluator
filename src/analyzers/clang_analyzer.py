import subprocess
import json
import re
import tempfile
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ClangIssue:
    severity: str
    type: str
    line: int
    column: int
    message: str
    category: str

class ClangTidyAnalyzer:
    def __init__(self):
        self.clang_available = self._check_clang_availability()
        self.kernel_checks = [
            'readability-*',
            'performance-*', 
            'bugprone-*',
            'security-*',
            'misc-*',
            '-readability-magic-numbers',  # disable some noisy checks
            '-readability-function-cognitive-complexity'
        ]
        
    def _check_clang_availability(self) -> bool:
        """check if clang-tidy is available"""
        try:
            result = subprocess.run(['clang-tidy', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def analyze_code(self, code: str, filename: str = "driver.c") -> Dict:
        """run clang-tidy analysis on code"""
        if not self.clang_available:
            return {"error": "clang-tidy not available", "fallback": True}
        
        # create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as temp_file:
            temp_file.write(code)
            temp_filepath = temp_file.name
        
        try:
            return self._run_clang_analysis(temp_filepath)
        finally:
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
    
    def _run_clang_analysis(self, filepath: str) -> Dict:
        """run clang-tidy and parse results"""
        
        # prepare clang-tidy command
        checks = ','.join(self.kernel_checks)
        cmd = [
            'clang-tidy',
            filepath,
            f'--checks={checks}',
            '--quiet',
            '--format-style=none',
            '--',
            '-I/usr/include',
            '-I/usr/src/linux-headers-generic/include',
            '-nostdinc',
            '-D__KERNEL__',
            '-DMODULE'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # parse clang-tidy output
            issues = self._parse_clang_output(result.stdout + result.stderr)
            
            return {
                "clang_available": True,
                "issues": issues,
                "analysis_successful": True,
                "raw_output": result.stdout + result.stderr,
                "summary": self._generate_summary(issues)
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "clang-tidy timeout", "clang_available": True}
        except Exception as e:
            return {"error": f"clang-tidy failed: {str(e)}", "clang_available": True}
    
    def _parse_clang_output(self, output: str) -> List[ClangIssue]:
        """parse clang-tidy output into structured issues"""
        issues = []
        
        # clang-tidy output format: file:line:col: severity: message [check-name]
        pattern = r'([^:]+):(\d+):(\d+):\s+(warning|error|note):\s+(.+?)\s+\[([^\]]+)\]'
        
        for match in re.finditer(pattern, output):
            filename, line, col, severity, message, check_name = match.groups()
            
            # categorize the issue
            category = self._categorize_issue(check_name, message)
            
            issues.append(ClangIssue(
                severity=severity,
                type=check_name,
                line=int(line),
                column=int(col),
                message=message.strip(),
                category=category
            ))
        
        return issues
    
    def _categorize_issue(self, check_name: str, message: str) -> str:
        """categorize clang issues by type"""
        
        if any(term in check_name.lower() for term in ['security', 'buffer', 'memory']):
            return 'security'
        elif any(term in check_name.lower() for term in ['performance', 'efficiency']):
            return 'performance'
        elif any(term in check_name.lower() for term in ['readability', 'style', 'naming']):
            return 'style'
        elif any(term in check_name.lower() for term in ['bugprone', 'bug', 'error']):
            return 'reliability'
        else:
            return 'general'
    
    def _generate_summary(self, issues: List[ClangIssue]) -> Dict:
        """generate summary statistics"""
        
        by_severity = {'error': 0, 'warning': 0, 'note': 0}
        by_category = {'security': 0, 'performance': 0, 'style': 0, 'reliability': 0, 'general': 0}
        
        for issue in issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_category[issue.category] = by_category.get(issue.category, 0) + 1
        
        # calculate clang score
        clang_score = self._calculate_clang_score(by_severity, by_category)
        
        return {
            'total_issues': len(issues),
            'by_severity': by_severity,
            'by_category': by_category,
            'clang_score': clang_score
        }
    
    def _calculate_clang_score(self, by_severity: Dict, by_category: Dict) -> float:
        """calculate score based on clang findings"""
        
        # severity weights
        severity_weights = {'error': 10, 'warning': 3, 'note': 1}
        
        # category weights  
        category_weights = {'security': 5, 'reliability': 4, 'performance': 3, 'style': 2, 'general': 1}
        
        # calculate penalty
        severity_penalty = sum(count * severity_weights.get(sev, 1) for sev, count in by_severity.items())
        category_penalty = sum(count * category_weights.get(cat, 1) for cat, count in by_category.items())
        
        total_penalty = severity_penalty + (category_penalty * 0.5)
        
        # base score 100, subtract penalties
        clang_score = max(0, 100 - total_penalty)
        
        return round(clang_score, 2)

class ClangInstaller:
    """helper class to install clang-tidy if missing"""
    
    @staticmethod
    def install_clang():
        """attempt to install clang-tidy"""
        try:
            print("attempting to install clang-tidy...")
            result = subprocess.run(['sudo', 'apt', 'install', '-y', 'clang-tidy'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("clang-tidy installed successfully")
                return True
            else:
                print(f"failed to install clang-tidy: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"error installing clang-tidy: {str(e)}")
            return False
    
    @staticmethod
    def check_and_install():
        """check for clang-tidy and install if missing"""
        analyzer = ClangTidyAnalyzer()
        
        if not analyzer.clang_available:
            print("clang-tidy not found")
            choice = input("install clang-tidy? (y/n): ").lower().strip()
            
            if choice == 'y':
                return ClangInstaller.install_clang()
            else:
                print("continuing without clang-tidy (fallback mode)")
                return False
        else:
            print("clang-tidy is available")
            return True
