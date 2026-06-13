import os
import re
import glob

def clean_main_py(file_path):
    print(f"Cleaning {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove verify_api_key_and_rate_limit function
    # Matches 'def verify_api_key_and_rate_limit...:' and everything indented under it
    # We look for a line starting with 'def verify_api_key_and_rate_limit' up to the next non-indented line.
    pattern_func = r'def verify_api_key_and_rate_limit.*?(?=\n[^\s#])'
    content = re.sub(pattern_func, '', content, flags=re.DOTALL)

    # 2. Remove RATE_LIMITS definitions
    content = re.sub(r'#.*rate limit.*\nRATE_LIMITS\s*=.*?\n', '', content, flags=re.IGNORECASE)
    content = re.sub(r'RATE_LIMITS\s*=.*?\n', '', content)

    # 3. Remove dependencies from decorators
    # Match ', dependencies=[Depends(verify_api_key_and_rate_limit)]'
    content = re.sub(r',\s*dependencies\s*=\s*\[\s*Depends\(\s*verify_api_key_and_rate_limit\s*\)\s*\]', '', content)
    # Match 'dependencies=[Depends(verify_api_key_and_rate_limit)], '
    content = re.sub(r'dependencies\s*=\s*\[\s*Depends\(\s*verify_api_key_and_rate_limit\s*\)\s*\]\s*,\s*', '', content)
    # Match 'dependencies=[Depends(verify_api_key_and_rate_limit)]' inside brackets without commas
    content = re.sub(r'dependencies\s*=\s*\[\s*Depends\(\s*verify_api_key_and_rate_limit\s*\)\s*\]', '', content)

    # 4. Clean up unused imports in main.py
    # Remove defaultdict import if it was imported for RATE_LIMITS
    content = re.sub(r'from collections import .*defaultdict.*\n', '', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def clean_test_main_py(file_path):
    if not os.path.exists(file_path):
        return
    print(f"Cleaning {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove whole test functions related to rate limiting or api keys
    # Matches def test_*rate_limit* up to next non-indented line
    pattern_test = r'def test_[a-zA-Z0-9_]*?(?:rate_limit|api_key)[a-zA-Z0-9_]*?\(.*?\):.*?(?=\n[^\s#]|\Z)'
    content = re.sub(pattern_test, '', content, flags=re.DOTALL)

    # 2. Remove references to RATE_LIMITS
    # Remove ', RATE_LIMITS' from imports
    content = re.sub(r',\s*RATE_LIMITS', '', content)
    content = re.sub(r'RATE_LIMITS\s*,\s*', '', content)
    # Remove lines containing RATE_LIMITS.clear()
    content = re.sub(r'.*RATE_LIMITS\.clear\(\).*\n', '', content)

    # 3. Remove lines managing API_KEYS in environment
    content = re.sub(r'.*os\.environ\[[\'"]API_KEYS[\'"]\].*\n', '', content)
    content = re.sub(r'.*os\.environ\.pop\([\'"]API_KEYS[\'"]\).*\n', '', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def clean_readme_md(file_path):
    if not os.path.exists(file_path):
        return
    print(f"Cleaning {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r'with Stripe key verification and rate limiting\.', 'service.', content, flags=re.IGNORECASE)
    content = re.sub(r'Stripe key verification and rate limiting', 'API service', content, flags=re.IGNORECASE)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    builds_dir = os.path.join(os.path.dirname(__file__), "builds")
    for folder in os.listdir(builds_dir):
        app_dir = os.path.join(builds_dir, folder)
        if not os.path.isdir(app_dir) or folder == "APIHub":
            continue
        
        main_path = os.path.join(app_dir, "main.py")
        test_path = os.path.join(app_dir, "test_main.py")
        readme_path = os.path.join(app_dir, "README.md")

        if os.path.exists(main_path):
            clean_main_py(main_path)
        if os.path.exists(test_path):
            clean_test_main_py(test_path)
        if os.path.exists(readme_path):
            clean_readme_md(readme_path)

if __name__ == "__main__":
    main()
