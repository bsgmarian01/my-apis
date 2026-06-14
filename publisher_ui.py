import os
import sys
import json
import requests
import subprocess
import shutil

# Rich UI imports
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint

console = Console()

CONFIG_PATH = "d:/Money_making/config.json"
BUILDS_DIR = "builds"

def load_hf_config():
    """Loads Hugging Face token and username from the config file."""
    config_path = "config.json"
    if not os.path.exists(config_path):
        config_path = CONFIG_PATH
        
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.json not found in workspace or fallback path.")
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    return config.get("HF_TOKEN"), config.get("HF_USERNAME")

def get_built_apis():
    """Scans builds directory and returns folder names of generated APIs."""
    if not os.path.exists(BUILDS_DIR):
        return []
    folders = []
    for d in os.listdir(BUILDS_DIR):
        full_path = os.path.join(BUILDS_DIR, d)
        if os.path.isdir(full_path) and d != "APIHub" and not d.startswith("."):
            if os.path.exists(os.path.join(full_path, "main.py")):
                folders.append(d)
    return sorted(folders)

def clean_old_hf_spaces(token, username, active_space_name):
    """Scans and deletes older devsuite-*-apis spaces on Hugging Face."""
    url = f"https://huggingface.co/api/spaces?author={username}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return
            
        spaces = res.json()
        for space in spaces:
            space_id = space.get("id", "")
            space_name = space_id.split("/")[-1]
            
            # Match devsuite-*-apis pattern
            if space_name.startswith("devsuite-") and space_name.endswith("-apis"):
                if space_name != active_space_name:
                    rprint(f"[bold yellow]Cleaning up old space: {space_name}...[/bold yellow]")
                    delete_url = "https://huggingface.co/api/repos/delete"
                    payload = {"name": space_name, "type": "space"}
                    requests.delete(delete_url, json=payload, headers=headers, timeout=15)
    except Exception as e:
        rprint(f"[bold red]Space cleanup warning: {e}[/bold red]")

def main():
    try:
        hf_token, hf_username = load_hf_config()
    except Exception as e:
        rprint(f"[bold red]Error loading config.json: {e}[/bold red]")
        sys.exit(1)

    while True:
        console.clear()
        rprint("[bold blue]╔═════════════════════════════════════════════════════════════════╗[/bold blue]")
        rprint("[bold blue]║                 ⚡ SELECTIVE JIT API PUBLISHER ⚡               ║[/bold blue]")
        rprint("[bold blue]╚═════════════════════════════════════════════════════════════════╝[/bold blue]\n")

        apis = get_built_apis()
        if not apis:
            rprint("[bold yellow]No generated APIs found in the builds directory.[/bold yellow]")
            Prompt.ask("\nPress Enter to exit...")
            break

        # 1. Show selectable APIs
        table = Table(title="Selectable APIs for Deployment Package", expand=True)
        table.add_column("Index", justify="center", style="cyan", width=6)
        table.add_column("API Folder Name", style="white")
        table.add_column("Directory Location", style="dim")
        
        for idx, api in enumerate(apis):
            table.add_row(str(idx + 1), api, os.path.join(BUILDS_DIR, api))
            
        console.print(table)
        print()

        # 2. Get Selection
        rprint("[bold yellow]To deploy multiple APIs in the same space, enter their indices separated by commas (e.g. 1,2,5).[/bold yellow]")
        rprint("[bold yellow]This ensures they are bundled together under the single devsuite-[N]-apis space.[/bold yellow]")
        selection = Prompt.ask(
            "Enter indices to deploy (e.g. 1,3,4), 'all' for everything, or 'q' to quit", 
            default="all"
        )

        if selection.strip().lower() == 'q':
            rprint("[bold blue]Goodbye![/bold blue]")
            break

        selected_apis = []
        if selection.strip().lower() == "all":
            selected_apis = apis
        else:
            try:
                indices = [int(i.strip()) - 1 for i in selection.split(",")]
                selected_apis = [apis[i] for i in indices if 0 <= i < len(apis)]
            except Exception:
                rprint("[bold red]Invalid selection indices. Press Enter to retry...[/bold red]")
                Prompt.ask("")
                continue

        if not selected_apis:
            rprint("[bold red]No valid APIs selected. Press Enter to retry...[/bold red]")
            Prompt.ask("")
            continue

        # 3. Choose Destination Target
        rprint("\n[bold cyan]Choose where you want to load the APIs:[/bold cyan]")
        rprint("  [bold cyan]1[/bold cyan] - GitHub Only")
        rprint("  [bold cyan]2[/bold cyan] - Hugging Face Only")
        rprint("  [bold cyan]3[/bold cyan] - Both GitHub and Hugging Face")
        rprint("  [bold cyan]C[/bold cyan] - Cancel and return to menu")
        target_choice = Prompt.ask("Select option", choices=["1", "2", "3", "C", "c"], default="3").upper()

        if target_choice == "C":
            continue

        num_apis = len(selected_apis)
        target_space_name = f"devsuite-{num_apis}-apis"

        if target_choice in ["2", "3"]:
            rprint(f"\n[bold cyan]Target Hugging Face Space Name:[/bold cyan] [bold yellow]{target_space_name}[/bold yellow]")
        rprint(f"[bold cyan]Deploying {num_apis} APIs:[/bold cyan] [dim]{', '.join(selected_apis)}[/dim]\n")

        if not Confirm.ask("Proceed with the selected deployment target?"):
            rprint("[bold red]Cancelled. Returning to menu...[/bold red]")
            Prompt.ask("\nPress Enter to continue...")
            continue

        # 4. Compile Hub locally using only selected apps
        rprint("\n[bold yellow]1. Compiling selective APIHub...[/bold yellow]")
        import build_api_hub
        try:
            # Rebuild builds/APIHub using only selected folders (clears out old apps)
            build_api_hub.main(api_dirs_override=selected_apis)
            rprint("[bold green]✓ APIHub compiled successfully.[/bold green]")
        except Exception as e:
            rprint(f"[bold red]✗ Hub compilation failed: {e}[/bold red]")
            Prompt.ask("\nPress Enter to return to menu...")
            continue

        # 5. Stage and push selected APIs + APIHub to GitHub
        if target_choice in ["1", "3"]:
            rprint("\n[bold yellow]2. Selectively pushing files to GitHub...[/bold yellow]")
            try:
                # Stage the APIHub changes, including untracked and deleted files in builds/APIHub
                subprocess.run(["git", "add", "-A", "builds/APIHub"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Stage only the selected API builds folders
                for api in selected_apis:
                    subprocess.run(["git", "add", os.path.join(BUILDS_DIR, api)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                # Commit
                commit_msg = f"Selective JIT API deploy: {num_apis} services ({', '.join(selected_apis)})"
                subprocess.run(["git", "commit", "-m", commit_msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Push to origin main
                push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
                if push_res.returncode == 0:
                    rprint("[bold green]✓ Selective changes pushed to GitHub successfully.[/bold green]")
                else:
                    rprint(f"[bold red]✗ GitHub Push failed: {push_res.stderr}[/bold red]")
            except Exception as e:
                rprint(f"[bold red]✗ GitHub processing encountered an error: {e}[/bold red]")

        # 6. Deploy selectively-compiled APIHub to Hugging Face
        if target_choice in ["2", "3"]:
            rprint("\n[bold yellow]3. Deploying to Hugging Face Spaces...[/bold yellow]")
            try:
                from src.hf_deployer import HFDeployer
                deployer = HFDeployer(token=hf_token, username=hf_username)
                app_dir = os.path.join("builds", "APIHub")
                
                # Deploy under the name devsuite-[N]-apis
                live_url = deployer.deploy_space(target_space_name, app_dir)
                rprint(f"[bold green]✓ Unified Space deployed successfully![/bold green]")
                rprint(f"Space URL: [underline]https://huggingface.co/spaces/{hf_username.lower()}/{target_space_name.lower().replace('_', '-')}[/underline]")
                rprint(f"Direct API URL: [underline]{live_url}[/underline]")
                
                # Clean up older devsuite-*-apis spaces to keep account clean
                clean_old_hf_spaces(hf_token, hf_username, target_space_name)
            except Exception as e:
                rprint(f"[bold red]✗ Hugging Face deployment failed: {e}[/bold red]")

        rprint("\n[bold green]=== Deployment Process Completed ===[/bold green]")
        Prompt.ask("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
