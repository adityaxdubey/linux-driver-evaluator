import re
import json
from typing import Dict, List

class SecurityVulnerabilityScanner:
    def __init__(self):
        # fixed vulnerability patterns - removed invalid regex
        self.vulnerability_patterns = {
            'buffer_overflow': {
                'patterns': [r'strcpy\s*\(', r'strcat\s*\(', r'sprintf\s*\('],
                'severity': 'critical',
                'cwe': 'CWE-120'
            },
            'unsafe_functions': {
                'patterns': [r'gets\s*\(', r'scanf\s*\('],
                'severity': 'high', 
                'cwe': 'CWE-120'
            },
            'integer_overflow': {
                'patterns': [r'\w+\s*\+\s*\w+\s*>', r'size\s*\*\s*count'],
                'severity': 'medium',
                'cwe': 'CWE-190'
            },
            'missing_bounds_check': {
                'patterns': [r'copy_from_user\s*\([^)]*\)\s*;', r'\[\s*\w+\s*\]\s*='],
                'severity': 'medium',
                'cwe': 'CWE-119'
            },
            'uninitialized_variable': {
                'patterns': [r'static\s+\w+\s+\w+\s*;'],
                'severity': 'low',
                'cwe': 'CWE-457'
            }
        }
    
    def scan_vulnerabilities(self, code: str) -> Dict:
        """comprehensive security vulnerability scan"""
        
        vulnerabilities = []
        lines = code.split('\n')
        
        for vuln_type, vuln_data in self.vulnerability_patterns.items():
            for pattern in vuln_data['patterns']:
                try:
                    for match in re.finditer(pattern, code, re.IGNORECASE):
                        line_num = code[:match.start()].count('\n') + 1
                        
                        # get the actual line content for context
                        if 1 <= line_num <= len(lines):
                            line_content = lines[line_num - 1].strip()
                        else:
                            line_content = match.group()
                        
                        vulnerabilities.append({
                            'type': vuln_type,
                            'severity': vuln_data['severity'],
                            'cwe': vuln_data['cwe'],
                            'line': line_num,
                            'match': match.group(),
                            'line_content': line_content,
                            'recommendation': self._get_recommendation(vuln_type)
                        })
                except re.error as e:
                    print(f"regex error in pattern {pattern}: {e}")
                    continue
        
        return {
            'total_vulnerabilities': len(vulnerabilities),
            'by_severity': self._count_by_severity(vulnerabilities),
            'vulnerabilities': vulnerabilities,
            'security_score': self._calculate_security_score(vulnerabilities)
        }
    
    def _count_by_severity(self, vulns: List[Dict]) -> Dict:
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for vuln in vulns:
            severity = vuln.get('severity', 'low')
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _calculate_security_score(self, vulns: List[Dict]) -> float:
        """calculate security score based on vulnerabilities found"""
        if not vulns:
            return 100.0
        
        penalty_weights = {
            'critical': 25, 
            'high': 15, 
            'medium': 8, 
            'low': 3
        }
        
        total_penalty = sum(
            penalty_weights.get(vuln.get('severity', 'low'), 3) 
            for vuln in vulns
        )
        
        return max(0, 100 - total_penalty)
    
    def _get_recommendation(self, vuln_type: str) -> str:
        recommendations = {
            'buffer_overflow': 'use safe string functions: strncpy, strncat, snprintf',
            'unsafe_functions': 'replace with safer alternatives',
            'integer_overflow': 'add overflow checks before arithmetic operations',
            'missing_bounds_check': 'validate array indices and buffer sizes',
            'uninitialized_variable': 'initialize variables at declaration'
        }
        return recommendations.get(vuln_type, 'review code for security best practices')
