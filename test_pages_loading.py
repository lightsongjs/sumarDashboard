"""
Test script to verify all pages can be imported and loaded
"""

import sys
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def test_page_import(page_path):
    """Test if a page can be imported without errors"""
    page_name = page_path.name

    try:
        # Read the file content
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to compile the code
        compile(content, page_path.name, 'exec')

        print(f"{GREEN}✓{RESET} {page_name}: Syntax OK")
        return True, None

    except SyntaxError as e:
        error_msg = f"Syntax Error at line {e.lineno}: {e.msg}"
        print(f"{RED}✗{RESET} {page_name}: {error_msg}")
        return False, error_msg

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"{RED}✗{RESET} {page_name}: {error_msg}")
        return False, error_msg


def test_page_structure(page_path):
    """Test if page has required structure"""
    page_name = page_path.name

    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'has_streamlit_import': 'import streamlit' in content,
        'has_main_function': 'def main():' in content,
        'has_main_guard': 'if __name__ == "__main__":' in content,
        'has_page_config': 'st.set_page_config' in content,
        'has_data_check': 'st.session_state' in content
    }

    all_passed = all(checks.values())

    if all_passed:
        print(f"{GREEN}✓{RESET} {page_name}: Structure OK")
    else:
        print(f"{YELLOW}⚠{RESET} {page_name}: Missing components:")
        for check, passed in checks.items():
            if not passed:
                print(f"  - {check}")

    return all_passed, checks


def test_imports_execution(page_path):
    """Test if imports work by executing import section"""
    page_name = page_path.name

    try:
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract import statements (before first function definition)
        lines = content.split('\n')
        import_section = []

        for line in lines:
            stripped = line.strip()
            # Stop at first function or class definition
            if stripped.startswith('def ') or stripped.startswith('class '):
                break
            import_section.append(line)

        import_code = '\n'.join(import_section)

        # Create a namespace and execute imports
        namespace = {}
        exec(import_code, namespace)

        print(f"{GREEN}✓{RESET} {page_name}: All imports successful")
        return True, None

    except ImportError as e:
        error_msg = f"Import Error: {str(e)}"
        print(f"{RED}✗{RESET} {page_name}: {error_msg}")
        return False, error_msg

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"{YELLOW}⚠{RESET} {page_name}: {error_msg}")
        return False, error_msg


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TESTING NEW PRODUCT INSIGHTS PAGES")
    print("="*60 + "\n")

    # Find all new pages (6-9)
    pages_dir = project_root / "pages"
    new_pages = sorted([
        p for p in pages_dir.glob("[6-9]_*.py")
    ])

    if not new_pages:
        print(f"{RED}ERROR:{RESET} No new pages found in {pages_dir}")
        return

    print(f"Found {len(new_pages)} new pages to test:\n")

    results = {}

    for page_path in new_pages:
        print(f"\n{YELLOW}Testing:{RESET} {page_path.name}")
        print("-" * 60)

        # Test 1: Syntax and compilation
        syntax_ok, syntax_error = test_page_import(page_path)

        # Test 2: Structure
        structure_ok, structure_checks = test_page_structure(page_path)

        # Test 3: Imports execution
        imports_ok, import_error = test_imports_execution(page_path)

        results[page_path.name] = {
            'syntax': syntax_ok,
            'structure': structure_ok,
            'imports': imports_ok,
            'errors': {
                'syntax': syntax_error,
                'imports': import_error
            }
        }

        print()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60 + "\n")

    total_pages = len(results)
    passed_all = sum(1 for r in results.values() if r['syntax'] and r['imports'])

    for page_name, result in results.items():
        if result['syntax'] and result['imports']:
            status = f"{GREEN}✓ PASS{RESET}"
        else:
            status = f"{RED}✗ FAIL{RESET}"

        print(f"{status} - {page_name}")

        if not result['syntax'] and result['errors']['syntax']:
            print(f"       Syntax: {result['errors']['syntax']}")
        if not result['imports'] and result['errors']['imports']:
            print(f"       Imports: {result['errors']['imports']}")

    print(f"\n{GREEN}{passed_all}/{total_pages}{RESET} pages passed all tests")

    if passed_all == total_pages:
        print(f"\n{GREEN}🎉 All pages are ready!{RESET}")
        return 0
    else:
        print(f"\n{RED}⚠ Some pages have issues that need fixing{RESET}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
