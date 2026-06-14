import os
import subprocess
import shutil
import tempfile
from typing import Tuple

class Validator:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or tempfile.gettempdir()
        # Create a single, persistent validation venv so we don't recreate it in loops
        self.persistent_venv_dir = os.path.join(self.workspace_root, "jit_factory_shared_venv")
        self._ensure_persistent_venv()

    def _get_python_path(self, venv_dir: str) -> str:
        """Gets the path to the python executable based on OS."""
        if os.name == "nt":
            return os.path.join(venv_dir, "Scripts", "python.exe")
        return os.path.join(venv_dir, "bin", "python")

    def _ensure_persistent_venv(self):
        """Builds and primes the validation environment exactly once."""
        if not os.path.exists(self.persistent_venv_dir):
            os.makedirs(self.workspace_root, exist_ok=True)
            # Create the venv once
            subprocess.run(["python", "-m", "venv", self.persistent_venv_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Upgrade pip and pre-install core requirements to save time later
            python_path = self._get_python_path(self.persistent_venv_dir)
            subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run([python_path, "-m", "pip", "install", "fastapi", "uvicorn", "pytest", "httpx", "pytest-mock", "pytest-asyncio"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run_tests(self, main_code: str, test_code: str, requirements: str) -> Tuple[bool, str]:
        """
        Creates a temporary project directory, syncs files, runs pytest using
        the shared persistent environment, and returns (success_boolean, console_output).
        """
        # Create unique temp project directory for the code files
        project_dir = tempfile.mkdtemp(prefix="api_val_", dir=self.workspace_root)
        python_path = self._get_python_path(self.persistent_venv_dir)
        
        try:
            # Write target files
            with open(os.path.join(project_dir, "main.py"), "w", encoding="utf-8") as f:
                f.write(main_code)
            with open(os.path.join(project_dir, "test_main.py"), "w", encoding="utf-8") as f:
                f.write(test_code)
                
            # Parse out packages that need to be installed
            req_lines = requirements.split('\n')
            essentials = ["fastapi", "uvicorn", "pytest", "httpx", "pytest-mock", "pytest-asyncio"]
            for req in essentials:
                if not any(req in line.lower() for line in req_lines if line.strip()):
                    req_lines.append(req)
            
            with open(os.path.join(project_dir, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write('\n'.join(req_lines))

            # Clean environment copies to prevent virtual env leakage from parent process
            clean_env = os.environ.copy()
            clean_env.pop("VIRTUAL_ENV", None)
            clean_env.pop("PYTHONPATH", None)

            # Install any additional or missing requirements into the shared environment
            install_res = subprocess.run(
                [python_path, "-m", "pip", "install", "-r", os.path.join(project_dir, "requirements.txt")],
                capture_output=True,
                text=True,
                env=clean_env
            )
            if install_res.returncode != 0:
                return False, f"Dependency installation failed:\nSTDOUT:\n{install_res.stdout}\nSTDERR:\n{install_res.stderr}"

            # Run pytest explicitly via the isolated python path wrapper to block environment leaking
            test_res = subprocess.run(
                [python_path, "-m", "pytest", "test_main.py"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                env=clean_env
            )
            
            success = (test_res.returncode == 0)
            output = f"STDOUT:\n{test_res.stdout}\nSTDERR:\n{test_res.stderr}"
            return success, output

        finally:
            # Clean up the code files, but LEAVE the persistent venv completely intact
            shutil.rmtree(project_dir, ignore_errors=True)