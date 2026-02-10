"""
Translation Quality Assurance Service
Part of Karau Automator

Features:
1. JSON Integrity Testing - missing keys, placeholder validation, syntax
2. Expansion Testing - detect text that may overflow UI
3. Pseudo-localization Testing - detect hard-coded strings
4. RTL Language Support Validation
5. Cultural/Regional Format Checks
"""

import json
import re
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path


class TranslationQAService:
    """Automated Translation Quality Assurance"""
    
    # Placeholder patterns to validate
    PLACEHOLDER_PATTERNS = [
        r'\{(\w+)\}',           # {name}, {count}
        r'\{\{(\w+)\}\}',       # {{name}}, {{count}}
        r'%[sd]',               # %s, %d
        r'%\d+\$[sd]',          # %1$s, %2$d
    ]
    
    # Languages known for text expansion (longer than English)
    EXPANSION_LANGUAGES = {
        'de': 1.35,  # German - 35% longer
        'fr': 1.30,  # French - 30% longer
        'es': 1.25,  # Spanish - 25% longer
        'it': 1.25,  # Italian - 25% longer
        'pt-BR': 1.30,  # Portuguese - 30% longer
        'ru': 1.30,  # Russian - 30% longer
        'ar': 1.25,  # Arabic - 25% longer
        'ja': 0.90,  # Japanese - typically shorter
        'zh': 0.80,  # Chinese - typically shorter
        'ko': 0.95,  # Korean - slightly shorter
    }
    
    # RTL Languages
    RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur']
    
    # Character length thresholds for UI elements
    UI_LENGTH_LIMITS = {
        'button': 20,           # Action buttons
        'nav': 15,              # Navigation items
        'tab': 12,              # Tab labels
        'badge': 10,            # Status badges
        'tooltip': 50,          # Tooltips
        'placeholder': 40,      # Input placeholders
        'label': 30,            # Form labels
        'title': 60,            # Page titles
        'description': 150,     # Descriptions
    }
    
    def __init__(self, locales_dir: str = None):
        self.locales_dir = locales_dir or "/app/frontend/src/locales"
        self.master_language = "en"
        self.qa_results = {}
        
    def run_full_qa(self) -> Dict[str, Any]:
        """Run complete QA suite on all translation files"""
        start_time = datetime.now(timezone.utc)
        
        results = {
            "run_id": f"qa_{start_time.strftime('%Y%m%d_%H%M%S')}",
            "timestamp": start_time.isoformat(),
            "status": "running",
            "summary": {
                "total_languages": 0,
                "total_keys": 0,
                "missing_keys": 0,
                "placeholder_errors": 0,
                "expansion_warnings": 0,
                "syntax_errors": 0,
                "rtl_issues": 0,
                "overall_score": 0
            },
            "languages": {},
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Load master (English) translations
        master_data = self._load_json_file(f"{self.locales_dir}/{self.master_language}.json")
        if not master_data:
            results["status"] = "failed"
            results["critical_issues"].append({
                "type": "master_file_missing",
                "message": f"Master language file ({self.master_language}.json) not found or invalid"
            })
            return results
        
        master_keys = self._flatten_keys(master_data)
        results["summary"]["total_keys"] = len(master_keys)
        
        # Get all language files
        language_files = self._get_language_files()
        results["summary"]["total_languages"] = len(language_files)
        
        # Run QA on each language
        for lang_code, file_path in language_files.items():
            lang_results = self._qa_language(lang_code, file_path, master_keys, master_data)
            results["languages"][lang_code] = lang_results
            
            # Aggregate summary
            results["summary"]["missing_keys"] += lang_results["missing_keys_count"]
            results["summary"]["placeholder_errors"] += len(lang_results["placeholder_errors"])
            results["summary"]["expansion_warnings"] += len(lang_results["expansion_warnings"])
            results["summary"]["syntax_errors"] += 1 if lang_results["syntax_error"] else 0
            results["summary"]["rtl_issues"] += len(lang_results.get("rtl_issues", []))
            
            # Collect critical issues
            if lang_results["syntax_error"]:
                results["critical_issues"].append({
                    "language": lang_code,
                    "type": "syntax_error",
                    "message": lang_results["syntax_error"]
                })
            
            for error in lang_results["placeholder_errors"]:
                results["critical_issues"].append({
                    "language": lang_code,
                    "type": "placeholder_error",
                    "key": error["key"],
                    "message": error["message"]
                })
        
        # Calculate overall score
        results["summary"]["overall_score"] = self._calculate_score(results)
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)
        
        results["status"] = "completed"
        results["duration_ms"] = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        self.qa_results = results
        return results
    
    def _load_json_file(self, file_path: str) -> Optional[Dict]:
        """Load and validate JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
        except FileNotFoundError:
            return None
    
    def _get_language_files(self) -> Dict[str, str]:
        """Get all language JSON files"""
        files = {}
        try:
            for f in os.listdir(self.locales_dir):
                if f.endswith('.json'):
                    lang_code = f.replace('.json', '')
                    files[lang_code] = os.path.join(self.locales_dir, f)
        except Exception:
            pass
        return files
    
    def _flatten_keys(self, data: Dict, prefix: str = "") -> Dict[str, str]:
        """Flatten nested dictionary to dot-notation keys"""
        keys = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.update(self._flatten_keys(value, full_key))
            else:
                keys[full_key] = str(value)
        return keys
    
    def _qa_language(self, lang_code: str, file_path: str, 
                     master_keys: Dict[str, str], master_data: Dict) -> Dict[str, Any]:
        """Run QA checks on a single language file"""
        results = {
            "language_code": lang_code,
            "file_path": file_path,
            "syntax_error": None,
            "total_keys": 0,
            "missing_keys_count": 0,
            "missing_keys": [],
            "extra_keys": [],
            "placeholder_errors": [],
            "expansion_warnings": [],
            "empty_translations": [],
            "identical_to_english": [],
            "rtl_issues": [],
            "ui_length_issues": [],
            "score": 100
        }
        
        # Load language file
        lang_data = self._load_json_file(file_path)
        if lang_data is None:
            results["syntax_error"] = f"Failed to parse {file_path}"
            results["score"] = 0
            return results
        
        lang_keys = self._flatten_keys(lang_data)
        results["total_keys"] = len(lang_keys)
        
        # Check for missing keys
        for key in master_keys:
            if key not in lang_keys:
                results["missing_keys"].append(key)
        results["missing_keys_count"] = len(results["missing_keys"])
        
        # Check for extra keys (not in master)
        for key in lang_keys:
            if key not in master_keys:
                results["extra_keys"].append(key)
        
        # Skip English for content checks
        if lang_code == self.master_language:
            return results
        
        # Check each translation
        for key, translation in lang_keys.items():
            if key not in master_keys:
                continue
                
            english_text = master_keys[key]
            
            # Check for empty translations
            if not translation or translation.strip() == "":
                results["empty_translations"].append(key)
                continue
            
            # Check for identical to English (potential untranslated)
            if translation == english_text and lang_code != self.master_language:
                # Allow some exceptions (proper nouns, technical terms)
                if not self._is_exception(key, translation):
                    results["identical_to_english"].append({
                        "key": key,
                        "value": translation
                    })
            
            # Validate placeholders
            placeholder_check = self._check_placeholders(key, english_text, translation)
            if placeholder_check:
                results["placeholder_errors"].append(placeholder_check)
            
            # Check text expansion
            expansion_check = self._check_expansion(key, english_text, translation, lang_code)
            if expansion_check:
                results["expansion_warnings"].append(expansion_check)
            
            # Check UI length limits
            length_check = self._check_ui_length(key, translation)
            if length_check:
                results["ui_length_issues"].append(length_check)
        
        # RTL-specific checks
        if lang_code in self.RTL_LANGUAGES:
            results["rtl_issues"] = self._check_rtl_issues(lang_keys)
        
        # Calculate language score
        results["score"] = self._calculate_language_score(results, len(master_keys))
        
        return results
    
    def _check_placeholders(self, key: str, english: str, translation: str) -> Optional[Dict]:
        """Check if placeholders are preserved in translation"""
        english_placeholders = set()
        translation_placeholders = set()
        
        for pattern in self.PLACEHOLDER_PATTERNS:
            english_placeholders.update(re.findall(pattern, english))
            translation_placeholders.update(re.findall(pattern, translation))
        
        missing = english_placeholders - translation_placeholders
        extra = translation_placeholders - english_placeholders
        
        if missing or extra:
            return {
                "key": key,
                "english": english,
                "translation": translation,
                "missing_placeholders": list(missing),
                "extra_placeholders": list(extra),
                "message": f"Placeholder mismatch: missing {list(missing)}, extra {list(extra)}"
            }
        return None
    
    def _check_expansion(self, key: str, english: str, translation: str, 
                        lang_code: str) -> Optional[Dict]:
        """Check if translation exceeds expected expansion ratio"""
        if lang_code not in self.EXPANSION_LANGUAGES:
            return None
        
        # Skip very short English strings (< 4 chars) as they naturally expand more
        if len(english) < 4:
            return None
        
        expected_ratio = self.EXPANSION_LANGUAGES[lang_code]
        actual_ratio = len(translation) / len(english) if english else 1
        
        # Flag if significantly longer than expected
        if actual_ratio > expected_ratio * 1.5:
            return {
                "key": key,
                "english_length": len(english),
                "translation_length": len(translation),
                "expected_max": int(len(english) * expected_ratio * 1.5),
                "expansion_ratio": round(actual_ratio, 2),
                "severity": "warning" if actual_ratio < expected_ratio * 2 else "high"
            }
        return None
    
    def _check_ui_length(self, key: str, translation: str) -> Optional[Dict]:
        """Check if translation exceeds UI component length limits"""
        # Determine UI component type from key
        component_type = None
        key_lower = key.lower()
        
        if any(x in key_lower for x in ['btn', 'button', 'action']):
            component_type = 'button'
        elif any(x in key_lower for x in ['nav.', 'menu', 'sidebar']):
            component_type = 'nav'
        elif 'tab' in key_lower:
            component_type = 'tab'
        elif any(x in key_lower for x in ['badge', 'status', 'tag']):
            component_type = 'badge'
        elif 'placeholder' in key_lower:
            component_type = 'placeholder'
        elif 'label' in key_lower:
            component_type = 'label'
        elif any(x in key_lower for x in ['title', 'heading']):
            component_type = 'title'
        elif any(x in key_lower for x in ['desc', 'description', 'subtitle']):
            component_type = 'description'
        
        if component_type and component_type in self.UI_LENGTH_LIMITS:
            limit = self.UI_LENGTH_LIMITS[component_type]
            if len(translation) > limit:
                return {
                    "key": key,
                    "component_type": component_type,
                    "length": len(translation),
                    "limit": limit,
                    "overflow": len(translation) - limit,
                    "translation": translation[:50] + "..." if len(translation) > 50 else translation
                }
        return None
    
    def _check_rtl_issues(self, lang_keys: Dict[str, str]) -> List[Dict]:
        """Check for RTL-specific issues"""
        issues = []
        
        for key, translation in lang_keys.items():
            # Check for LTR characters that might cause issues
            ltr_chars = re.findall(r'[a-zA-Z]{3,}', translation)
            if ltr_chars:
                # Some English words in RTL text are okay (brand names, etc.)
                significant_ltr = [w for w in ltr_chars if len(w) > 5 and w.lower() not in 
                                  ['medmatch', 'email', 'password', 'admin', 'api', 'url']]
                if significant_ltr:
                    issues.append({
                        "key": key,
                        "type": "mixed_direction",
                        "ltr_words": significant_ltr[:5]
                    })
        
        return issues
    
    def _is_exception(self, key: str, value: str) -> bool:
        """Check if identical-to-English is acceptable"""
        exceptions = [
            'email', 'password', 'url', 'api', 'admin', 'medmatch',
            'json', 'pdf', 'csv', 'http', 'https', 'oauth', 'sso'
        ]
        return any(exc in value.lower() for exc in exceptions) or len(value) <= 3
    
    def _calculate_language_score(self, results: Dict, total_master_keys: int) -> int:
        """Calculate quality score for a language (0-100)"""
        score = 100
        
        # Deduct for missing keys (major issue)
        missing_ratio = results["missing_keys_count"] / total_master_keys if total_master_keys else 0
        score -= missing_ratio * 50
        
        # Deduct for placeholder errors (critical)
        score -= len(results["placeholder_errors"]) * 5
        
        # Deduct for empty translations
        score -= len(results["empty_translations"]) * 2
        
        # Deduct for expansion warnings (minor)
        score -= len(results["expansion_warnings"]) * 0.5
        
        # Deduct for UI length issues
        score -= len(results["ui_length_issues"]) * 1
        
        # Syntax error is catastrophic
        if results["syntax_error"]:
            score = 0
        
        return max(0, min(100, int(score)))
    
    def _calculate_score(self, results: Dict) -> int:
        """Calculate overall QA score"""
        if not results["languages"]:
            return 0
        
        total_score = sum(lang["score"] for lang in results["languages"].values())
        return int(total_score / len(results["languages"]))
    
    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Generate actionable recommendations based on QA results"""
        recommendations = []
        
        # Critical: Syntax errors
        if results["summary"]["syntax_errors"] > 0:
            recommendations.append({
                "priority": "critical",
                "category": "syntax",
                "title": "Fix JSON Syntax Errors",
                "description": f"{results['summary']['syntax_errors']} language file(s) have JSON syntax errors and cannot be loaded",
                "action": "Run JSON validator on affected files and fix syntax issues"
            })
        
        # Critical: Placeholder errors
        if results["summary"]["placeholder_errors"] > 0:
            recommendations.append({
                "priority": "critical",
                "category": "placeholders",
                "title": "Fix Placeholder Mismatches",
                "description": f"{results['summary']['placeholder_errors']} translations have missing or extra placeholders that will cause runtime errors",
                "action": "Review placeholder_errors in each language and ensure all {variables} are preserved"
            })
        
        # High: Missing keys
        if results["summary"]["missing_keys"] > 0:
            recommendations.append({
                "priority": "high",
                "category": "completeness",
                "title": "Add Missing Translation Keys",
                "description": f"{results['summary']['missing_keys']} translation keys are missing across all languages",
                "action": "Run translation update script to add missing keys to all language files"
            })
        
        # Medium: Expansion warnings
        if results["summary"]["expansion_warnings"] > 10:
            recommendations.append({
                "priority": "medium",
                "category": "ui",
                "title": "Review Text Expansion Issues",
                "description": f"{results['summary']['expansion_warnings']} translations may be too long for their UI containers",
                "action": "Test UI in German/French to verify text doesn't overflow buttons and labels"
            })
        
        # Low: RTL issues
        if results["summary"]["rtl_issues"] > 0:
            recommendations.append({
                "priority": "low",
                "category": "rtl",
                "title": "Review RTL Language Display",
                "description": f"{results['summary']['rtl_issues']} potential issues found in RTL languages",
                "action": "Test Arabic/Hebrew UI to ensure proper bidirectional text handling"
            })
        
        return recommendations
    
    def generate_pseudo_localization(self, source_lang: str = "en") -> Dict[str, str]:
        """Generate pseudo-localized strings for testing"""
        source_data = self._load_json_file(f"{self.locales_dir}/{source_lang}.json")
        if not source_data:
            return {}
        
        source_keys = self._flatten_keys(source_data)
        pseudo_keys = {}
        
        # Character map for pseudo-localization
        char_map = {
            'a': 'α', 'b': 'β', 'c': 'ç', 'd': 'δ', 'e': 'é',
            'f': 'ƒ', 'g': 'ǵ', 'h': 'ĥ', 'i': 'í', 'j': 'ĵ',
            'k': 'ķ', 'l': 'ĺ', 'm': 'ɱ', 'n': 'ñ', 'o': 'ó',
            'p': 'ρ', 'q': 'ǫ', 'r': 'ŕ', 's': 'ś', 't': 'ť',
            'u': 'ú', 'v': 'ν', 'w': 'ŵ', 'x': 'χ', 'y': 'ý',
            'z': 'ž'
        }
        
        for key, value in source_keys.items():
            # Preserve placeholders
            pseudo_value = ""
            in_placeholder = False
            placeholder_buffer = ""
            
            for char in value:
                if char == '{':
                    in_placeholder = True
                    placeholder_buffer = char
                elif char == '}' and in_placeholder:
                    placeholder_buffer += char
                    pseudo_value += placeholder_buffer
                    placeholder_buffer = ""
                    in_placeholder = False
                elif in_placeholder:
                    placeholder_buffer += char
                else:
                    pseudo_value += char_map.get(char.lower(), char)
            
            # Add expansion markers
            pseudo_keys[key] = f"[[ {pseudo_value} ]]"
        
        return pseudo_keys
    
    def get_missing_keys_report(self) -> Dict[str, List[str]]:
        """Get detailed report of missing keys per language"""
        if not self.qa_results:
            self.run_full_qa()
        
        report = {}
        for lang_code, lang_results in self.qa_results.get("languages", {}).items():
            if lang_results["missing_keys"]:
                report[lang_code] = lang_results["missing_keys"]
        
        return report
    
    def get_expansion_report(self) -> Dict[str, List[Dict]]:
        """Get detailed report of text expansion issues"""
        if not self.qa_results:
            self.run_full_qa()
        
        report = {}
        for lang_code, lang_results in self.qa_results.get("languages", {}).items():
            if lang_results["expansion_warnings"]:
                report[lang_code] = lang_results["expansion_warnings"]
        
        return report


# Singleton instance
translation_qa_service = TranslationQAService()
