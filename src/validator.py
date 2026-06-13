import os
import subprocess
import shutil
import tempfile
from typing import Tuple

class Validator:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or tempfile.gettempdir()

    def run_tests(self, main_code: str, test_code: str, requirements: str) -> Tuple[bool, str]:
        """
        Creates a temporary project environment, installs requirements, runs pytest,
        and returns (success_boolean, console_output).
        """
        # Create unique temp project directory
        project_dir = tempfile.mkdtemp(prefix="api_val_", dir=self.workspace_root)
        try:
            # Write files
            with open(os.path.join(project_dir, "main.py"), "w", encoding="utf-8") as f:
                f.write(main_code)
            with open(os.path.join(project_dir, "test_main.py"), "w", encoding="utf-8") as f:
                f.write(test_code)
            # Ensure essential test and application dependencies are present
            req_lines = requirements.split('\n')
            essentials = ["fastapi", "uvicorn", "pytest", "httpx"]
            for req in essentials:
                if not any(req in line.lower() for line in req_lines if line.strip()):
                    req_lines.append(req)
            
            with open(os.path.join(project_dir, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write('\n'.join(req_lines))

            # Setup local virtual environment inside the temp project directory
            venv_dir = os.path.join(project_dir, "venv")
            subprocess.run(["python", "-m", "venv", venv_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Determine python path depending on OS
            if os.name == "nt":
                python_path = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                python_path = os.path.join(venv_dir, "bin", "python")

            # Install dependencies
            install_res = subprocess.run(
                [python_path, "-m", "pip", "install", "-r", os.path.join(project_dir, "requirements.txt")],
                capture_output=True,
                text=True
            )
            if install_res.returncode != 0:
                return False, f"Dependency installation failed:\nSTDOUT:\n{install_res.stdout}\nSTDERR:\n{install_res.stderr}"

            # Run pytest
            test_res = subprocess.run(
                [python_path, "-m", "pytest", "test_main.py"],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            
            success = (test_res.returncode == 0)
            output = f"STDOUT:\n{test_res.stdout}\nSTDERR:\n{test_res.stderr}"
            return success, output

        finally:
            # Clean up temp directory
            shutil.rmtree(project_dir, ignore_errors=True)
