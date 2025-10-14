#!/usr/bin/env python3
"""
Test script to verify Resume Agent setup
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import openai
        print("✅ OpenAI library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False
    
    try:
        import langchain
        print("✅ LangChain library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LangChain: {e}")
        return False
    
    try:
        import google.auth
        print("✅ Google Auth library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Google Auth: {e}")
        return False
    
    try:
        import click
        print("✅ Click library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Click: {e}")
        return False
    
    return True

def test_files():
    """Test that required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'config.py',
        'main.py',
        'requirements.txt',
        'data/base_resume.txt',
        'env.example'
    ]
    
    required_dirs = [
        'agents',
        'integrations',
        'utils',
        'data'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_good = False
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ {dir_path}/ directory exists")
        else:
            print(f"❌ {dir_path}/ directory missing")
            all_good = False
    
    return all_good

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        print("✅ Configuration module loaded successfully")
        
        # Check if .env file exists
        if os.path.exists('.env'):
            print("✅ .env file exists")
        else:
            print("⚠️  .env file not found (copy from env.example)")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Resume Agent Setup Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("File Structure Test", test_files),
        ("Configuration Test", test_config)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and add your API keys")
        print("2. Edit data/base_resume.txt with your resume")
        print("3. Run: python main.py --test")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()

