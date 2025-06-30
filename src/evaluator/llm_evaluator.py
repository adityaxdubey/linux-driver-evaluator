import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class LLMEvalCriteria:
    name: str
    weight: float
    description: str
    max_score: float

class LLMBasedEvaluator:
    def __init__(self):
        self.evaluation_criteria = [
            LLMEvalCriteria("code_correctness", 0.30, "functional correctness and logic", 100.0),
            LLMEvalCriteria("kernel_compliance", 0.25, "adherence to kernel coding standards", 100.0),
            LLMEvalCriteria("security_awareness", 0.20, "security best practices", 100.0),
            LLMEvalCriteria("code_quality", 0.15, "maintainability and readability", 100.0),
            LLMEvalCriteria("innovation", 0.10, "creative and efficient solutions", 100.0)
        ]
        
    def evaluate_generated_code(self, code: str, prompt: str, model_metadata: Dict) -> Dict:
        """comprehensive LLM-generated code evaluation"""
        
        results = {
            'prompt_analysis': self._analyze_prompt_complexity(prompt),
            'code_analysis': self._analyze_generated_code(code),
            'prompt_adherence': self._evaluate_prompt_adherence(code, prompt),
            'llm_specific_metrics': self._calculate_llm_metrics(code, prompt, model_metadata),
            'comparative_analysis': self._comparative_analysis(code, prompt)
        }
        
        results['llm_evaluation_score'] = self._calculate_llm_score(results)
        return results
    
    def _analyze_prompt_complexity(self, prompt: str) -> Dict:
        """analyze the complexity and specificity of the prompt"""
        
        complexity_indicators = {
            'technical_terms': len(re.findall(r'\b(driver|kernel|module|device|interrupt|DMA|mutex|spinlock)\b', prompt.lower())),
            'specific_requirements': len(re.findall(r'\b(must|should|implement|support|handle)\b', prompt.lower())),
            'constraints': len(re.findall(r'\b(without|avoid|prevent|ensure|guarantee)\b', prompt.lower())),
            'word_count': len(prompt.split())
        }
        
        # calculate prompt complexity score
        complexity_score = min(100, (
            complexity_indicators['technical_terms'] * 10 +
            complexity_indicators['specific_requirements'] * 8 +
            complexity_indicators['constraints'] * 12 +
            complexity_indicators['word_count'] * 0.5
        ))
        
        return {
            'complexity_indicators': complexity_indicators,
            'complexity_score': complexity_score,
            'prompt_category': self._categorize_prompt(prompt)
        }
    
    def _analyze_generated_code(self, code: str) -> Dict:
        """deep analysis of LLM-generated code characteristics"""
        
        code_characteristics = {
            'length_metrics': {
                'total_lines': len(code.split('\n')),
                'code_lines': len([line for line in code.split('\n') if line.strip() and not line.strip().startswith('//')]),
                'comment_lines': len([line for line in code.split('\n') if line.strip().startswith('//')])
            },
            'structure_metrics': {
                'function_count': len(re.findall(r'^\s*(?:static\s+)?\w+\s+\w+\s*\([^)]*\)\s*{', code, re.MULTILINE)),
                'struct_count': len(re.findall(r'\bstruct\s+\w+', code)),
                'include_count': len(re.findall(r'#include', code))
            },
            'kernel_specificity': {
                'kernel_functions': len(re.findall(r'\b(kmalloc|kfree|copy_from_user|copy_to_user|printk)\b', code)),
                'kernel_headers': len(re.findall(r'#include\s*<linux/', code)),
                'module_macros': len(re.findall(r'\b(MODULE_LICENSE|MODULE_AUTHOR|module_init|module_exit)\b', code))
            },
            'error_handling': {
                'error_returns': len(re.findall(r'return\s+-E[A-Z]+', code)),
                'null_checks': len(re.findall(r'if\s*\([^)]*==\s*NULL\)', code)),
                'error_goto': len(re.findall(r'goto\s+\w*err\w*', code))
            }
        }
        
        return {
            'characteristics': code_characteristics,
            'code_quality_score': self._calculate_code_quality_score(code_characteristics),
            'llm_signature_analysis': self._analyze_llm_signatures(code)
        }
    
    def _evaluate_prompt_adherence(self, code: str, prompt: str) -> Dict:
        """evaluate how well the code follows the prompt requirements"""
        
        # extract key requirements from prompt
        requirements = self._extract_requirements(prompt)
        
        adherence_scores = {}
        for req_type, req_keywords in requirements.items():
            matches = sum(1 for keyword in req_keywords if keyword.lower() in code.lower())
            adherence_scores[req_type] = min(100, (matches / max(1, len(req_keywords))) * 100)
        
        overall_adherence = sum(adherence_scores.values()) / max(1, len(adherence_scores))
        
        return {
            'requirements_extracted': requirements,
            'adherence_by_category': adherence_scores,
            'overall_adherence_score': overall_adherence,
            'missing_requirements': self._identify_missing_requirements(code, requirements)
        }
    
    def _calculate_llm_metrics(self, code: str, prompt: str, model_metadata: Dict) -> Dict:
        """calculate LLM-specific evaluation metrics"""
        
        # analyze response appropriateness
        response_metrics = {
            'prompt_to_code_ratio': len(code) / max(1, len(prompt)),
            'completeness_score': self._calculate_completeness(code),
            'coherence_score': self._calculate_coherence(code),
            'specificity_score': self._calculate_specificity(code, prompt)
        }
        
        # model-specific analysis
        model_analysis = {
            'model_name': model_metadata.get('model', 'unknown'),
            'tokens_used': model_metadata.get('tokens_used', 0),
            'generation_time': model_metadata.get('generation_time', 0),
            'efficiency_score': self._calculate_generation_efficiency(model_metadata)
        }
        
        return {
            'response_metrics': response_metrics,
            'model_analysis': model_analysis,
            'llm_score': self._calculate_overall_llm_score(response_metrics, model_analysis)
        }
    
    def _comparative_analysis(self, code: str, prompt: str) -> Dict:
        """compare against expected patterns and best practices"""
        
        # define ideal patterns for different prompt types
        ideal_patterns = {
            'character_driver': ['file_operations', 'cdev_init', 'register_chrdev', 'copy_from_user'],
            'platform_driver': ['platform_driver', 'probe', 'remove', 'platform_device'],
            'basic_module': ['module_init', 'module_exit', 'MODULE_LICENSE']
        }
        
        prompt_type = self._categorize_prompt(prompt)
        expected_patterns = ideal_patterns.get(prompt_type, [])
        
        pattern_matches = sum(1 for pattern in expected_patterns if pattern in code)
        pattern_score = (pattern_matches / max(1, len(expected_patterns))) * 100
        
        return {
            'prompt_type': prompt_type,
            'expected_patterns': expected_patterns,
            'patterns_found': pattern_matches,
            'pattern_completeness_score': pattern_score,
            'best_practices_score': self._evaluate_best_practices(code)
        }
    
    def _calculate_llm_score(self, results: Dict) -> float:
        """calculate overall LLM evaluation score"""
        
        component_scores = {
            'prompt_adherence': results['prompt_adherence']['overall_adherence_score'],
            'code_quality': results['code_analysis']['code_quality_score'],
            'llm_metrics': results['llm_specific_metrics']['llm_score'],
            'comparative': results['comparative_analysis']['pattern_completeness_score']
        }
        
        weights = {'prompt_adherence': 0.35, 'code_quality': 0.30, 'llm_metrics': 0.20, 'comparative': 0.15}
        
        weighted_score = sum(score * weights[component] for component, score in component_scores.items())
        return round(weighted_score, 2)
    
    # Helper methods
    def _categorize_prompt(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if 'character' in prompt_lower and 'driver' in prompt_lower:
            return 'character_driver'
        elif 'platform' in prompt_lower and 'driver' in prompt_lower:
            return 'platform_driver'
        elif 'module' in prompt_lower:
            return 'basic_module'
        else:
            return 'generic'
    
    def _extract_requirements(self, prompt: str) -> Dict:
        requirements = {
            'functions': re.findall(r'\b(read|write|open|close|ioctl|probe|remove)\b', prompt.lower()),
            'features': re.findall(r'\b(interrupt|dma|buffer|device|register)\b', prompt.lower()),
            'constraints': re.findall(r'\b(error.handling|memory.management|thread.safe)\b', prompt.lower())
        }
        return requirements
    
    def _calculate_completeness(self, code: str) -> float:
        essential_elements = ['include', 'function', 'return', 'module_init', 'module_exit']
        present_elements = sum(1 for element in essential_elements if element in code.lower())
        return (present_elements / len(essential_elements)) * 100
    
    def _calculate_coherence(self, code: str) -> float:
        # simple coherence check based on structure
        has_proper_structure = all(pattern in code for pattern in ['{', '}', '(', ')'])
        has_logical_flow = 'module_init' in code and 'module_exit' in code
        coherence_score = 50 + (25 if has_proper_structure else 0) + (25 if has_logical_flow else 0)
        return coherence_score
    
    def _calculate_specificity(self, code: str, prompt: str) -> float:
        prompt_keywords = set(re.findall(r'\b\w+\b', prompt.lower()))
        code_keywords = set(re.findall(r'\b\w+\b', code.lower()))
        overlap = len(prompt_keywords.intersection(code_keywords))
        return min(100, (overlap / max(1, len(prompt_keywords))) * 100)
    
    def _calculate_generation_efficiency(self, model_metadata: Dict) -> float:
        tokens = model_metadata.get('tokens_used', 1000)
        time = model_metadata.get('generation_time', 10)
        efficiency = min(100, (1000 / tokens) * (10 / max(1, time)) * 100)
        return efficiency
    
    def _calculate_overall_llm_score(self, response_metrics: Dict, model_analysis: Dict) -> float:
        response_score = sum(response_metrics.values()) / len(response_metrics)
        efficiency_score = model_analysis['efficiency_score']
        return (response_score * 0.7 + efficiency_score * 0.3)
    
    def _evaluate_best_practices(self, code: str) -> float:
        best_practices = [
            'static' in code,  # proper scoping
            'const' in code,   # immutability where appropriate
            'MODULE_LICENSE' in code,  # licensing
            'error' in code.lower() or 'return -' in code,  # error handling
            len(re.findall(r'//.*', code)) > 0  # comments
        ]
        return (sum(best_practices) / len(best_practices)) * 100
    
    def _identify_missing_requirements(self, code: str, requirements: Dict) -> List[str]:
        missing = []
        for category, req_list in requirements.items():
            for req in req_list:
                if req not in code.lower():
                    missing.append(f"{category}: {req}")
        return missing
    
    def _analyze_llm_signatures(self, code: str) -> Dict:
        """analyze patterns that might indicate AI generation"""
        signatures = {
            'verbose_comments': len(re.findall(r'//.*\b(this|here|we|function|method)\b', code, re.IGNORECASE)),
            'generic_names': len(re.findall(r'\b(device|driver|module|test|example)\b', code)),
            'placeholder_patterns': len(re.findall(r'\b(TODO|FIXME|XXX|placeholder)\b', code, re.IGNORECASE)),
            'overly_structured': len(re.findall(r'^\s*/\*\*', code, re.MULTILINE))
        }
        return signatures
    
    def _calculate_code_quality_score(self, characteristics: Dict) -> float:
        length = characteristics['length_metrics']['code_lines']
        functions = characteristics['structure_metrics']['function_count']
        kernel_funcs = characteristics['kernel_specificity']['kernel_functions']
        
        # balance between completeness and conciseness
        length_score = min(100, max(0, 100 - abs(length - 50) * 2))  # ideal around 50 lines
        structure_score = min(100, functions * 25)  # bonus for having functions
        kernel_score = min(100, kernel_funcs * 20)  # bonus for kernel-specific code
        
        return (length_score + structure_score + kernel_score) / 3
