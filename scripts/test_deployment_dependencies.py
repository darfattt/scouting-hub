#!/usr/bin/env python3
"""
Test script to verify all deployment dependencies are included in requirements.txt.
"""

import os
import sys
import ast
import re

# Add src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Change to project root directory
os.chdir(project_root)

def extract_imports_from_file(file_path):
    """Extract all import statements from a Python file."""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to extract imports
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get the top-level module name
                    module_name = alias.name.split('.')[0]
                    imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get the top-level module name
                    module_name = node.module.split('.')[0]
                    imports.add(module_name)
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return imports

def get_all_python_files():
    """Get all Python files in the project."""
    python_files = []
    
    # Check main files
    main_files = ['app.py']
    for file in main_files:
        if os.path.exists(file):
            python_files.append(file)
    
    # Check src directory
    src_dir = 'src'
    if os.path.exists(src_dir):
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    
    return python_files

def get_requirements():
    """Get requirements from requirements.txt."""
    requirements = set()
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove version specifiers
                    package = re.split(r'[>=<!=]', line)[0].strip()
                    requirements.add(package)
    except FileNotFoundError:
        print("requirements.txt not found")
    
    return requirements

def test_import_availability():
    """Test that all required imports are available."""
    print("🔍 TESTING IMPORT AVAILABILITY")
    print("-" * 50)
    
    # Standard library modules that don't need to be in requirements.txt
    stdlib_modules = {
        'os', 'sys', 'datetime', 'typing', 'ast', 're', 'json', 'csv', 
        'collections', 'itertools', 'functools', 'pathlib', 'time',
        'warnings', 'inspect', 'traceback', 'copy', 'math', 'random'
    }
    
    # Get all Python files
    python_files = get_all_python_files()
    print(f"Found {len(python_files)} Python files to analyze")
    
    # Extract all imports
    all_imports = set()
    for file_path in python_files:
        file_imports = extract_imports_from_file(file_path)
        all_imports.update(file_imports)
        print(f"  {file_path}: {len(file_imports)} unique imports")
    
    # Filter out standard library modules
    third_party_imports = all_imports - stdlib_modules
    
    print(f"\nFound {len(third_party_imports)} third-party imports:")
    for imp in sorted(third_party_imports):
        print(f"  - {imp}")
    
    # Get requirements
    requirements = get_requirements()
    print(f"\nFound {len(requirements)} packages in requirements.txt:")
    for req in sorted(requirements):
        print(f"  - {req}")
    
    # Check for missing requirements
    missing_requirements = third_party_imports - requirements
    extra_requirements = requirements - third_party_imports
    
    if missing_requirements:
        print(f"\n❌ Missing from requirements.txt:")
        for req in sorted(missing_requirements):
            print(f"  - {req}")
        return False
    else:
        print(f"\n✅ All third-party imports are in requirements.txt")
    
    if extra_requirements:
        print(f"\n⚠️ Extra packages in requirements.txt (not imported):")
        for req in sorted(extra_requirements):
            print(f"  - {req}")
    
    return True

def test_specific_imports():
    """Test specific imports that are known to be used."""
    print("\n🔍 TESTING SPECIFIC IMPORTS")
    print("-" * 50)
    
    critical_imports = [
        'pandas',
        'numpy', 
        'streamlit',
        'matplotlib',
        'seaborn',
        'plotly',
        'scipy',
        'sklearn'
    ]
    
    all_available = True
    
    for package in critical_imports:
        try:
            __import__(package)
            print(f"✅ {package} - Available")
        except ImportError as e:
            print(f"❌ {package} - Not available: {e}")
            all_available = False
    
    return all_available

def test_plotly_submodules():
    """Test plotly submodules that are specifically used."""
    print("\n🔍 TESTING PLOTLY SUBMODULES")
    print("-" * 50)
    
    plotly_modules = [
        'plotly.graph_objects',
        'plotly.express',
        'plotly.subplots'
    ]
    
    all_available = True
    
    for module in plotly_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError as e:
            print(f"❌ {module} - Not available: {e}")
            all_available = False
    
    return all_available

def test_scipy_submodules():
    """Test scipy submodules that are specifically used."""
    print("\n🔍 TESTING SCIPY SUBMODULES")
    print("-" * 50)
    
    scipy_modules = [
        'scipy.stats'
    ]
    
    all_available = True
    
    for module in scipy_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError as e:
            print(f"❌ {module} - Not available: {e}")
            all_available = False
    
    return all_available

def test_sklearn_submodules():
    """Test sklearn submodules that might be used."""
    print("\n🔍 TESTING SKLEARN SUBMODULES")
    print("-" * 50)
    
    sklearn_modules = [
        'sklearn.preprocessing',
        'sklearn.metrics'
    ]
    
    all_available = True
    
    for module in sklearn_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError as e:
            print(f"ℹ️ {module} - Not available (may not be used): {e}")
            # Don't mark as failure since these might not be used
    
    return all_available

def main():
    """Main test function."""
    print("=" * 80)
    print("DEPLOYMENT DEPENDENCIES VERIFICATION")
    print("=" * 80)
    print("Testing all dependencies required for Streamlit Cloud deployment")
    print()
    
    # Test 1: Import availability
    import_test_passed = test_import_availability()
    
    # Test 2: Specific imports
    specific_test_passed = test_specific_imports()
    
    # Test 3: Plotly submodules
    plotly_test_passed = test_plotly_submodules()
    
    # Test 4: Scipy submodules
    scipy_test_passed = test_scipy_submodules()
    
    # Test 5: Sklearn submodules
    sklearn_test_passed = test_sklearn_submodules()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_tests_passed = (import_test_passed and specific_test_passed and 
                       plotly_test_passed and scipy_test_passed and
                       sklearn_test_passed)
    
    if import_test_passed:
        print("✅ Import availability: All third-party imports in requirements.txt")
    else:
        print("❌ Import availability: Missing packages in requirements.txt")
    
    if specific_test_passed:
        print("✅ Specific imports: All critical packages available")
    else:
        print("❌ Specific imports: Some critical packages missing")
    
    if plotly_test_passed:
        print("✅ Plotly submodules: All available")
    else:
        print("❌ Plotly submodules: Some missing")
    
    if scipy_test_passed:
        print("✅ Scipy submodules: All available")
    else:
        print("❌ Scipy submodules: Some missing")
    
    if sklearn_test_passed:
        print("✅ Sklearn submodules: Available")
    else:
        print("ℹ️ Sklearn submodules: Some not available (may not be critical)")
    
    print()
    
    if all_tests_passed:
        print("🎉 SUCCESS! All deployment dependencies are properly configured.")
        print("\nCurrent requirements.txt:")
        requirements = get_requirements()
        for req in sorted(requirements):
            print(f"  - {req}")
        print("\nDeployment status:")
        print("- ✅ All critical packages included")
        print("- ✅ Plotly and submodules available")
        print("- ✅ Scipy and submodules available")
        print("- ✅ No missing third-party dependencies")
        print("\nNext steps:")
        print("1. Deploy to Streamlit Cloud")
        print("2. All visualization and analysis features should work")
        print("3. Only AI Assistant will be disabled (as expected)")
    else:
        print("💥 FAILED! Some dependency issues found.")
        print("\nPlease fix the issues above before deploying.")
        print("\nCommon fixes:")
        print("1. Add missing packages to requirements.txt")
        print("2. Check package names and spelling")
        print("3. Verify import statements in code")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
