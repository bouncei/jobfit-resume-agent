#!/usr/bin/env python3
"""
Test script for Google Docs authentication
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from integrations.google_docs import GoogleDocsClient


def test_authentication():
    """Test Google Docs authentication and connection"""
    print("🔍 Testing Google Docs Authentication\n")
    
    try:
        # Initialize client
        client = GoogleDocsClient()
        
        # Check authentication status
        print("📊 Checking authentication status...")
        status = client.check_authentication_status()
        
        print(f"Token exists: {status['token_exists']}")
        print(f"Token valid: {status['token_valid']}")
        print(f"Token expired: {status['token_expired']}") 
        print(f"Needs refresh: {status['needs_refresh']}")
        print(f"Needs reauth: {status['needs_reauth']}")
        print(f"Authenticated: {status['authenticated']}\n")
        
        # Attempt authentication
        print("🔐 Attempting authentication...")
        success = client.authenticate()
        
        if success:
            print("✅ Authentication successful!")
            
            # Test connection by creating a simple test document
            print("📄 Testing document creation...")
            test_doc = client.create_document("Test Document - Auth Verification")
            
            print(f"✅ Test document created successfully!")
            print(f"📄 Document ID: {test_doc['document_id']}")
            print(f"🔗 Document URL: {test_doc['document_url']}")
            
            return True
        else:
            print("❌ Authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication test: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
