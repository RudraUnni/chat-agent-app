# security_config/input_validation.py
"""
Input validation and sanitization for Open WebUI v0.6.5 integration
Helps mitigate XSS and injection vulnerabilities
"""

import re
import html
import bleach
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Allowed HTML tags for medical content (very restrictive)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'width', 'height']
}

# Medical-specific patterns that should be allowed
MEDICAL_PATTERNS = {
    'dosage': r'\d+(\.\d+)?\s*(mg|g|ml|mcg|units?|iu)\b',
    'vital_signs': r'\d+\/\d+\s*mmHg|\d+\s*bpm|\d+(\.\d+)?\s*°[CF]',
    'lab_values': r'\d+(\.\d+)?\s*(mg\/dl|mmol\/L|g\/dl|%)',
    'medical_codes': r'[A-Z]\d{2}(\.\d{1,2})?|CPT\s*\d{5}|ICD-\d+'
}


class MedicalInputValidator:
    """Validator for medical content in Open WebUI integration"""
    
    def __init__(self):
        self.max_length = 10000  # Maximum input length
        self.blocked_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',                # JavaScript URLs
            r'on\w+\s*=',                 # Event handlers
            r'data:text/html',            # Data URLs with HTML
            r'vbscript:',                 # VBScript
            r'expression\s*\(',           # CSS expressions
        ]
    
    def sanitize_html(self, content: str) -> str:
        """Sanitize HTML content while preserving medical formatting"""
        if not content:
            return ""
        
        # First pass: Remove dangerous patterns
        for pattern in self.blocked_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Second pass: Use bleach for comprehensive sanitization
        cleaned = bleach.clean(
            content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return cleaned
    
    def validate_user_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize user input for Open WebUI"""
        validated = {}
        
        for key, value in input_data.items():
            if isinstance(value, str):
                # Length check
                if len(value) > self.max_length:
                    logger.warning(f"Input too long for field {key}: {len(value)} chars")
                    value = value[:self.max_length]
                
                # Sanitize content
                if key in ['message', 'content', 'prompt']:
                    validated[key] = self.sanitize_medical_content(value)
                else:
                    validated[key] = self.sanitize_html(value)
            
            elif isinstance(value, (int, float, bool)):
                validated[key] = value
            
            elif isinstance(value, dict):
                validated[key] = self.validate_user_input(value)
            
            elif isinstance(value, list):
                validated[key] = [
                    self.validate_user_input(item) if isinstance(item, dict)
                    else self.sanitize_html(str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                validated[key] = str(value)
        
        return validated
    
    def sanitize_medical_content(self, content: str) -> str:
        """Specialized sanitization for medical content"""
        # Preserve medical patterns while sanitizing
        medical_placeholders = {}
        placeholder_counter = 0
        
        # Extract and preserve medical patterns
        for pattern_name, pattern in MEDICAL_PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                placeholder = f"__MEDICAL_PATTERN_{placeholder_counter}__"
                medical_placeholders[placeholder] = match.group()
                content = content.replace(match.group(), placeholder)
                placeholder_counter += 1
        
        # Sanitize the content
        sanitized = self.sanitize_html(content)
        
        # Restore medical patterns
        for placeholder, original in medical_placeholders.items():
            sanitized = sanitized.replace(placeholder, original)
        
        return sanitized
    
    def validate_model_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Open WebUI model request"""
        validated = self.validate_user_input(request_data)
        
        # Additional validation for model requests
        if 'model' in validated:
            allowed_models = ['medical-assistant', 'pubmed-research', 'medical-analysis']
            if validated['model'] not in allowed_models:
                logger.warning(f"Invalid model requested: {validated['model']}")
                validated['model'] = 'medical-assistant'
        
        if 'temperature' in validated:
            temp = float(validated.get('temperature', 0.7))
            validated['temperature'] = max(0.0, min(2.0, temp))
        
        if 'max_tokens' in validated:
            max_tokens = int(validated.get('max_tokens', 1000))
            validated['max_tokens'] = max(1, min(4000, max_tokens))
        
        return validated


# Singleton instance
medical_validator = MedicalInputValidator()


def validate_openwebui_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Main validation function for Open WebUI inputs"""
    try:
        return medical_validator.validate_user_input(data)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return {"error": "Invalid input data"}


def validate_model_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validation function for model requests"""
    try:
        return medical_validator.validate_model_request(data)
    except Exception as e:
        logger.error(f"Model request validation error: {str(e)}")
        return {"error": "Invalid model request"}


# Rate limiting helper
class RateLimiter:
    """Simple rate limiter for API requests"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limiting"""
        import time
        current_time = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[client_ip]) < self.max_requests:
            self.requests[client_ip].append(current_time)
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=60, window_seconds=60)