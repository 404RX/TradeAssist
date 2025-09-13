#!/usr/bin/env python3
"""
Test script to verify log sanitization is working correctly
"""

import logging
import tempfile
import os
from logging_config import SanitizingFormatter, sanitize_sensitive_data

def test_sanitization_patterns():
    """Test the sanitization patterns directly"""
    print("Testing sanitization patterns...")
    
    test_cases = [
        # API Keys
        ("API Key: PKTEST123456789012345", "API Key: PK***REDACTED***"),
        ("Secret: AKTEST123456789012345", "Secret: AK***REDACTED***"),
        ("Token: SKTEST123456789012345", "Token: SK***REDACTED***"),
        
        # Long tokens
        ("Bearer abc123def456ghi789jkl012mno345pqr678stu901vwx234yz", "Bearer ***REDACTED_TOKEN***"),
        
        # UUIDs (Account IDs)
        ("Account: 34626f04-0ffe-4f7a-b52e-607e8ddbd04c", "Account: ***REDACTED_UUID***"),
        
        # JWT tokens
        ("JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c", "JWT: ***REDACTED_JWT***"),
        
        # Authorization headers
        ('Authorization: Bearer abc123def456', 'Authorization: Bearer ***REDACTED***'),
        ('Authorization: abc123def456', 'Authorization: ***REDACTED***'),
        
        # JSON secrets
        ('{"api_key": "secret123", "token": "token456"}', '"api_key": "***REDACTED***"'),
    ]
    
    all_passed = True
    for original, expected in test_cases:
        sanitized = sanitize_sensitive_data(original)
        passed = expected.replace('"***REDACTED***"', '"***REDACTED***"') in sanitized
        
        if passed:
            print(f"✓ PASS: '{original[:50]}...' -> sanitized")
        else:
            print(f"✗ FAIL: '{original}' -> '{sanitized}' (expected to contain '{expected}')")
            all_passed = False
    
    return all_passed

def test_logger_sanitization():
    """Test that loggers properly sanitize sensitive data"""
    print("\nTesting logger sanitization...")
    
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log') as tmp_file:
        log_file = tmp_file.name
    
    try:
        # Set up a test logger with sanitizing formatter
        test_logger = logging.getLogger('test_sanitization')
        test_logger.setLevel(logging.INFO)
        test_logger.handlers.clear()  # Clear any existing handlers
        
        # Add file handler with sanitizing formatter
        handler = logging.FileHandler(log_file)
        formatter = SanitizingFormatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        test_logger.addHandler(handler)
        test_logger.propagate = False  # Prevent propagation to root logger
        
        # Log some sensitive data
        sensitive_messages = [
            "API connection failed with key PKTEST123456789012345",
            "Account 34626f04-0ffe-4f7a-b52e-607e8ddbd04c has balance $1000",
            "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature",
            'Request payload: {"api_key": "secret123", "account": "12345"}',
            "Trading with secret AKTEST987654321098765 on live account"
        ]
        
        for msg in sensitive_messages:
            test_logger.info(msg)
        
        # Close the handler to ensure all data is written
        handler.close()
        test_logger.removeHandler(handler)
        
        # Read the log file and check for sensitive data
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        print("Log file contents:")
        print("-" * 50)
        print(log_content)
        print("-" * 50)
        
        # Check that sensitive patterns are NOT present in raw form
        sensitive_patterns = [
            "PKTEST123456789012345",
            "AKTEST987654321098765", 
            "34626f04-0ffe-4f7a-b52e-607e8ddbd04c",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature",
            '"secret123"'
        ]
        
        found_sensitive = []
        for pattern in sensitive_patterns:
            if pattern in log_content:
                found_sensitive.append(pattern)
        
        if found_sensitive:
            print(f"✗ FAIL: Found sensitive data in logs: {found_sensitive}")
            return False
        else:
            print("✓ PASS: No sensitive data found in logs")
            return True
            
    finally:
        # Clean up temp file
        if os.path.exists(log_file):
            os.unlink(log_file)

def main():
    """Run all sanitization tests"""
    print("=" * 60)
    print("LOG SANITIZATION TEST SUITE")
    print("=" * 60)
    
    # Test sanitization patterns
    patterns_passed = test_sanitization_patterns()
    
    # Test logger integration
    logger_passed = test_logger_sanitization()
    
    print("\n" + "=" * 60)
    if patterns_passed and logger_passed:
        print("✓ ALL TESTS PASSED - Log sanitization is working correctly!")
        print("✓ API keys, secrets, and sensitive data will be redacted from logs")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Log sanitization needs fixing")
        return 1

if __name__ == "__main__":
    exit(main())