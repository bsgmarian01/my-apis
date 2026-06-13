import os
import subprocess
import sys

def main():
    print("=== Running APIHub Tests ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    hub_dir = os.path.join(base_dir, "builds", "APIHub")
    
    # Create virtual environment in APIHub if it doesn't exist
    venv_dir = os.path.join(hub_dir, "venv")
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    
    # Python executable in venv
    if os.name == "nt":
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        pytest_bin = os.path.join(venv_dir, "Scripts", "pytest.exe")
    else:
        python_bin = os.path.join(venv_dir, "bin", "python")
        pytest_bin = os.path.join(venv_dir, "bin", "pytest")
        
    print("Installing requirements...")
    # Clean up requirements (e.g. remove comment line with 'httpx2' if it exists/failed, wait, is httpx2 in requirements? No, it's just httpx)
    reqs_file = os.path.join(hub_dir, "requirements.txt")
    # Let's read and clean up the requirements file if any invalid lines are in there
    with open(reqs_file, "r") as f:
        lines = f.readlines()
    
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if not l or l.startswith("#"):
            continue
        if "httpx2" in l: # Ignore non-existent package
            continue
        cleaned_lines.append(l)
        
    with open(reqs_file, "w") as f:
        f.write("\n".join(cleaned_lines) + "\n")
        
    # Install
    subprocess.run([python_bin, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([python_bin, "-m", "pip", "install", "-r", reqs_file], check=True)
    
    print("Running pytest...")
    res = subprocess.run([python_bin, "-m", "pytest", "test_main.py"], cwd=hub_dir, capture_output=True, text=True)
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
    
    if res.returncode == 0:
        print("SUCCESS")
    else:
        print("FAILED")

if __name__ == "__main__":
    main()
