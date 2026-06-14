import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime

# Import modules from workspace
from demand_finder import search_reddit_demand, load_registry, save_registry
from api_generator import generate_api_code, load_runpod_config
import publish_new_api

# Rich UI imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import print as rprint

console = Console()

BUILDS_DIR = "builds"

def get_runpod_status(endpoint):
    """Checks if the RunPod/Ollama endpoint is reachable."""
    try:
        url = f"{endpoint.rstrip('/')}/api/tags"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return "[bold green]ONLINE[/bold green]"
        return f"[bold yellow]OFFLINE (HTTP {res.status_code})[/bold yellow]"
    except Exception:
        return "[bold red]OFFLINE (Unreachable)[/bold red]"

def print_header(endpoint, model):
    console.clear()
    banner = Text()
    banner.append("╔═════════════════════════════════════════════════════════════════╗\n", style="bold blue")
    banner.append("║                    ⚡ JIT API FACTORY v2.5 ⚡                    ║\n", style="bold cyan")
    banner.append("║                  [ DIRECTOR CONTROLS ACTIVE ]                   ║\n", style="bold green")
    banner.append("╚═════════════════════════════════════════════════════════════════╝", style="bold blue")
    rprint(banner)
    
    # Render Status
    status_str = get_runpod_status(endpoint)
    rprint(f"[bold cyan]RunPod LLM Status:[/bold cyan] {status_str} | [dim]{endpoint} ({model})[/dim]")
    print()

def get_status_style(status):
    if status in ["success", "built", "active"]:
        return "bold green"
    elif status in ["pending", "running"]:
        return "bold yellow"
    elif status in ["error", "failed"]:
        return "bold red"
    return "white"

def show_main_menu(endpoint, model):
    print_header(endpoint, model)
    
    registry = load_registry()
    ideas = registry.get("ideas", [])
    apis = registry.get("apis", [])
    
    # Statistics
    stats_table = Table(title="Factory Overview", title_style="bold magenta", expand=True)
    stats_table.add_column("Scraped Demands", justify="center", style="cyan")
    stats_table.add_column("APIs Generated", justify="center", style="green")
    stats_table.add_column("Standalone Builds", justify="center", style="yellow")
    
    stats_table.add_row(str(len(ideas)), str(len(apis)), str(len(apis)))
    console.print(stats_table)
    print()

    # Menu Options
    console.print("[bold cyan]COMMAND CENTER:[/bold cyan]")
    rprint(" [1] 🔍 [bold blue]Scan for API Demands[/bold blue] (Reddit/StackOverflow)")
    rprint(" [2] 📋 [bold yellow]Review Scraped Ideas & Build[/bold yellow]")
    rprint(" [3] 🔨 [bold green]Build a Custom API[/bold green] (Manual Prompt)")
    rprint(" [4] 📊 [bold white]View Generated APIs & Build Logs[/bold white]")
    rprint(" [5] ❌ [bold red]Exit[/bold red]")
    print()
    
    choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"], default="2")
    return choice

def handle_scan(endpoint, model):
    print_header(endpoint, model)
    with console.status("[bold yellow]Scanning subreddits for developer demand...[/bold yellow]", spinner="bouncingBar"):
        new_ideas, total = search_reddit_demand()
    
    rprint(f"\n[bold green]Scan Completed Successfully![/bold green]")
    rprint(f"Total matching posts found: [bold cyan]{total}[/bold cyan]")
    rprint(f"New demands appended to registry: [bold green]{new_ideas}[/bold green]")
    input("\nPress Enter to return to main menu...")

def handle_review_ideas(endpoint, model):
    print_header(endpoint, model)
    registry = load_registry()
    ideas = registry.get("ideas", [])
    
    if not ideas:
        rprint("[bold yellow]No ideas found in the registry. Try running a scan first![/bold yellow]")
        input("\nPress Enter to return...")
        return

    table = Table(title="Scraped API Demands (Unmet Need)", expand=True)
    table.add_column("Index", justify="center", style="cyan", width=6)
    table.add_column("Source", style="blue", width=15)
    table.add_column("Title", style="white")
    table.add_column("Date Found", style="yellow", width=20)
    
    pending_ideas = [idea for idea in ideas if idea.get("status", "pending") == "pending"]
    
    if not pending_ideas:
        rprint("[bold green]All scraped ideas have been processed! Great job Director.[/bold green]")
        input("\nPress Enter to return...")
        return

    for idx, idea in enumerate(pending_ideas):
        table.add_row(
            str(idx + 1),
            idea.get("source", "N/A"),
            idea.get("title", ""),
            idea.get("timestamp", "")[:19].replace("T", " ")
        )
        
    console.print(table)
    print()
    
    choice = Prompt.ask("Enter the Index to build, or 'C' to cancel", default="C")
    if choice.upper() == "C":
        return
        
    try:
        selected_idx = int(choice) - 1
        if selected_idx < 0 or selected_idx >= len(pending_ideas):
            rprint("[bold red]Invalid Index.[/bold red]")
            time.sleep(1.5)
            return
            
        selected_idea = pending_ideas[selected_idx]
        build_api_flow(selected_idea["title"], selected_idea["description"], endpoint, model, selected_idea)
    except ValueError:
        rprint("[bold red]Invalid input.[/bold red]")
        time.sleep(1.5)

def handle_build_custom(endpoint, model):
    print_header(endpoint, model)
    console.print("[bold green]🔨 CREATE CUSTOM API[/bold green]")
    api_name = Prompt.ask("Enter the API Name (e.g., Chicago Scrap Metal Prices)")
    api_desc = Prompt.ask("Enter the description and endpoint requirements")
    build_api_flow(api_name, api_desc, endpoint, model)

def build_api_flow(api_name, api_desc, endpoint, model, associated_idea=None):
    print_header(endpoint, model)
    rprint(f"[bold cyan]Reviewing specifications for:[/bold cyan] [bold white]{api_name}[/bold white]")
    rprint(f"[dim]{api_desc}[/dim]\n")
    
    # Checkpoint 1: Code Generation and Testing
    if not Confirm.ask("Start local build generation and self-debugging loop?"):
        return
        
    print_header(endpoint, model)
    
    # 1. Run JIT LLM generation loop with live UI logs
    rprint("[bold yellow]1. Running JIT generation and self-debugging loop...[/bold yellow]")
    
    def ui_log_callback(msg, level):
        if level == "success":
            rprint(f"[bold green]✓ {msg}[/bold green]")
        elif level == "warning":
            rprint(f"[bold yellow]⚠ {msg}[/bold yellow]")
        elif level == "error":
            rprint(f"[bold red]✗ {msg}[/bold red]")
        elif level == "debug":
            rprint(f"[dim cyan]{msg}[/dim cyan]")
        else:
            rprint(f"[bold blue]i {msg}[/bold blue]")

    api_res = generate_api_code(api_name, api_desc, ui_callback=ui_log_callback)
    
    if not api_res.get("success"):
        rprint(f"[bold red]✗ API Build Failed:[/bold red] {api_res.get('error')}")
        input("\nPress Enter to return...")
        return

    folder_name = os.path.basename(api_res.get("directory"))
    rprint(f"\n[bold green]✓ Local Build Successful![/bold green] Files saved in [dim]builds/{folder_name}[/dim]")
    
    # Checkpoint 2: Separate Production Deployment Authorization
    pub_success = False
    pub_msg = "Skipped publication stage (Local Only)"
    
    if Confirm.ask(f"Would you like to publish '{folder_name}' to GitHub & Hugging Face production?"):
        rprint(f"\n[bold yellow]2. Selectively publishing '{folder_name}' to GitHub & Hugging Face...[/bold yellow]")
        with console.status("[bold blue]Publishing new API...[/bold blue]"):
            pub_success, pub_msg = publish_new_api.publish_api(api_name, folder_name)
            
        if pub_success:
            rprint(f"[bold green]✓ Publishing Complete:[/bold green]\n{pub_msg}")
        else:
            rprint(f"[bold red]✗ Publishing Failed:[/bold red] {pub_msg}")
    else:
        rprint("\n[bold yellow]⏸ Deployment deferred. Code remains safe in your local sandbox directory.[/bold yellow]")

    # 3. Log accurate asset states into registry
    registry = load_registry()
    new_api_record = {
        "api_name": api_name,
        "description": api_desc,
        "timestamp": datetime.now().isoformat(),
        "directory": api_res.get("directory"),
        "files": api_res.get("files", []),
        "status": "success" if (pub_success or pub_msg.startswith("Skipped")) else "failed",
        "error": None if (pub_success or pub_msg.startswith("Skipped")) else pub_msg
    }
    
    registry["apis"].append(new_api_record)
    
    # Mark associated idea as processed
    if associated_idea:
        for idea in registry["ideas"]:
            if idea["id"] == associated_idea["id"]:
                # If kept local, mark as 'built_local', otherwise 'built'
                idea["status"] = "built" if pub_success else "built_local"
                break
                
    save_registry(registry)
    input("\nPress Enter to return...")

def handle_compile_deploy_manually(endpoint, model):
    print_header(endpoint, model)
    rprint("[bold yellow]Compiling local builds and deploying to Hugging Face...[/bold yellow]\n")
    try:
        build_api_hub.main()
        rprint("\n[bold green]✓ Compilation Complete![/bold green]")
        deploy_hub.main()
        rprint("\n[bold green]✓ Hugging Face Space Updated successfully![/bold green]")
    except Exception as e:
        rprint(f"\n[bold red]✗ Action failed:[/bold red] {e}")
    input("\nPress Enter to return...")

def handle_view_apis(endpoint, model):
    print_header(endpoint, model)
    registry = load_registry()
    apis = registry.get("apis", [])
    
    if not apis:
        rprint("[bold yellow]No APIs have been generated yet.[/bold yellow]")
        input("\nPress Enter to return...")
        return
        
    table = Table(title="Generated APIs and Build Logs", expand=True)
    table.add_column("API Name", style="cyan", width=25)
    table.add_column("Status", width=10)
    table.add_column("Directory", style="dim", width=25)
    table.add_column("Created At", style="yellow")
    table.add_column("Errors", style="red")
    
    for api in apis:
        status_style = get_status_style(api.get("status"))
        table.add_row(
            api.get("api_name", ""),
            Text(api.get("status", "").upper(), style=status_style),
            api.get("directory", ""),
            api.get("timestamp", "")[:19].replace("T", " "),
            api.get("error", "None") or "None"
        )
        
    console.print(table)
    input("\nPress Enter to return to main menu...")

def main():
    os.makedirs(BUILDS_DIR, exist_ok=True)
    
    # Read Ollama config
    config_data = load_runpod_config()
    endpoint = config_data.get("LLM_ENDPOINT")
    model = config_data.get("LLM_MODEL")

    while True:
        choice = show_main_menu(endpoint, model)
        if choice == "1":
            handle_scan(endpoint, model)
        elif choice == "2":
            handle_review_ideas(endpoint, model)
        elif choice == "3":
            handle_build_custom(endpoint, model)
        elif choice == "4":
            handle_view_apis(endpoint, model)
        elif choice == "5":
            rprint("\n[bold green]Goodbye Director. Powering down Factory...[/bold green]")
            sys.exit(0)

if __name__ == "__main__":
    main()
