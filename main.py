import os
import sys
import json
from src.llm_client import LLMClient
from src.planner import Planner
from src.generator import Generator
from src.validator import Validator
from src.deployer import Deployer
from src.publisher import Publisher

# Configuration (Read from config.json or env variables)
config_path = os.path.join(os.path.dirname(__file__), "config.json")
config = {}
if os.path.exists(config_path):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception:
        pass

OLLAMA_ENDPOINT = os.getenv("LLM_ENDPOINT", config.get("LLM_ENDPOINT", "https://k8k7jsxqre0keg-11434.proxy.runpod.net"))
HF_TOKEN = config.get("HF_TOKEN", "")
HF_USERNAME = config.get("HF_USERNAME", "")
STRIPE_LINK = config.get("STRIPE_LINK", "")
LLM_MODEL = config.get("LLM_MODEL", "qwen2.5-coder:32b-instruct-q4_K_M")

def main():
    print("=== Starting Autonomous API Factory ===")
    
    # Initialize client and modules
    llm = LLMClient(endpoint=OLLAMA_ENDPOINT, model=LLM_MODEL)
    planner = Planner(llm)
    generator = Generator(llm)
    validator = Validator()
    
    # 1. Plan an API
    print("\n[Step 1] Planning a new high-utility micro-API...")
    try:
        api_idea = planner.generate_api_idea()
        print(f"API Idea generated successfully: {api_idea.get('title')}")
        print(f"Description: {api_idea.get('description')}")
    except Exception as e:
        print(f"Error during planning phase: {e}")
        sys.exit(1)

    # 2. Generate and Self-Debug Codebase
    print("\n[Step 2] Generating FastAPI codebase and pytest test suite...")
    try:
        main_code, test_code, reqs = generator.generate_codebase(api_idea, stripe_link=STRIPE_LINK)
    except Exception as e:
        print(f"Error generating codebase: {e}")
        sys.exit(1)

    print("\n[Step 3] Running validation and self-debugging loop...")
    max_debug_attempts = 10
    validated = False
    
    for attempt in range(1, max_debug_attempts + 1):
        print(f"--- Running tests (Attempt {attempt}/{max_debug_attempts}) ---")
        success, test_log = validator.run_tests(main_code, test_code, reqs)
        
        if success:
            print("Tests passed successfully!")
            validated = True
            break
        else:
            print(f"Tests failed! Traceback:\n{test_log}")
            print(f"Sending console output to Qwen for debugging...")
            if attempt < max_debug_attempts:
                try:
                    main_code, test_code, reqs = generator.debug_codebase(
                        main_code=main_code,
                        test_code=test_code,
                        requirements=reqs,
                        test_output=test_log,
                        stripe_link=STRIPE_LINK
                    )
                except Exception as dbg_err:
                    print(f"Debugging iteration error: {dbg_err}")
                    break
            else:
                print("Exceeded maximum debugging attempts. Code validation failed.")

    if not validated:
        print("Could not generate a working, error-free API. Exiting.")
        sys.exit(1)

    # Save final validated code locally
    output_dir = os.path.join("builds", api_idea.get("name", "GeneratedAPI"))
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "main.py"), "w", encoding="utf-8") as f:
        f.write(main_code)
    with open(os.path.join(output_dir, "test_main.py"), "w", encoding="utf-8") as f:
        f.write(test_code)
    with open(os.path.join(output_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write(reqs)
    
    print(f"\nSuccessfully saved validated codebase in local folder: {output_dir}")

    # Re-build the unified APIHub to merge the new API
    print("\n[Step 3.5] Rebuilding unified APIHub with new API...")
    import build_api_hub
    try:
        build_api_hub.main()
    except Exception as build_err:
        print(f"Failed to rebuild APIHub: {build_err}")
        sys.exit(1)

    # 3. Deployment to Hugging Face Spaces
    if HF_TOKEN and HF_USERNAME:
        print("\n[Step 4] Starting Hugging Face Space deployment (devsuite-apis)...")
        from src.hf_deployer import HFDeployer
        deployer = HFDeployer(token=HF_TOKEN, username=HF_USERNAME)
        try:
            live_url = deployer.deploy_space("devsuite-apis", os.path.join("builds", "APIHub"))
            print(f"Unified APIHub deployed successfully to Hugging Face!")
            print(f"Live API URL: {live_url}")
            print(f"Space URL: https://huggingface.co/spaces/{HF_USERNAME.lower()}/devsuite-apis")
        except Exception as deploy_err:
            print(f"Hugging Face deployment failed: {deploy_err}")
            sys.exit(1)
    else:
        print("\nSkipping live deployment (HF_TOKEN or HF_USERNAME not configured in config.json).")

    print("\n=== Process Completed ===")

if __name__ == "__main__":
    main()
