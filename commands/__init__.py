"""
Command management module.

This module provides a mechanism to register and handle slash commands
within the CLI interface. It also includes default command implementations.
"""

import sys
from typing import Callable, Any
from rich.console import Console

console = Console(color_system="truecolor", width=120)

# Dictionary to register commands
# Key: command name (e.g., "help", "exit")
# Value: dict containing 'description' and 'function'
COMMANDS: dict[str, dict[str, Any]] = {}

def register_command(name: str, description: str) -> Callable:
    """
    Decorator to register a new slash command.

    Args:
        name (str): The name of the command (e.g., "help").
        description (str): A brief description of what the command does.

    Returns:
        Callable: The decorator function.
    """
    def decorator(func: Callable) -> Callable:
        COMMANDS[name.lower()] = {
            "description": description,
            "function": func
        }
        return func
    return decorator

def handle_command(user_input: str) -> bool:
    """
    Process and execute user input if it is a slash command.

    Args:
        user_input (str): The raw input string from the user.

    Returns:
        bool: True if a slash command was processed, False otherwise.
    """
    text = user_input.strip()
    if not text.startswith("/"):
        return False

    parts = text[1:].split(maxsplit=1)
    cmd_name = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd_name in COMMANDS:
        try:
            COMMANDS[cmd_name]["function"](args)
        except Exception as e:
            console.print(f"  [bold red]Error executing command /{cmd_name}: {e}[/]")
    else:
        console.print(f"  [bold red]Invalid command:[/] /{cmd_name}. Type `/help` to see the list of available commands.")
    
    return True

# --- Default Commands Registration ---

@register_command("help", "Display the list of available commands")
def cmd_help(args: str) -> None:
    """Handle the '/help' command."""
    console.print("  [bold #00F0FF]Available commands:[/]")
    for name, info in sorted(COMMANDS.items()):
        console.print(f"    [bold #00A3FF]/{name}[/]: {info['description']}")

@register_command("clear", "Clear the console screen")
def cmd_clear(args: str) -> None:
    """Handle the '/clear' command."""
    console.clear()

@register_command("exit", "Exit the Pumen Agent application")
def cmd_exit(args: str) -> None:
    """Handle the '/exit' command."""
    console.print("  [bold red]Goodbye![/]")
    sys.exit(0)

@register_command("model", "View or change the active AI Model")
def cmd_model(args: str) -> None:
    """Handle the '/model' command."""
    import cli.chat
    from providers import get_available_models
    
    selected_model = args.strip()
    
    # Get models for current provider
    available_models = get_available_models(cli.chat.CURRENT_PROVIDER)
    
    if not selected_model:
        console.print(f"  [bold green]Current active model:[/] [bold yellow]{cli.chat.CURRENT_MODEL}[/]")
        console.print("  [italic gray]To change the model: Type [bold]/model [/] (include the space) and select from the dropdown menu![/]")
    else:
        if selected_model in available_models:
            old_model = cli.chat.CURRENT_MODEL
            if old_model != selected_model:
                cli.chat.CURRENT_MODEL = selected_model
                cli.chat.save_user_config(cli.chat.CURRENT_PROVIDER, cli.chat.CURRENT_MODEL)
                console.print(f"  [bold green]Model switched:[/] [bold gray]{old_model}[/] ➔ [bold yellow]{cli.chat.CURRENT_MODEL}[/]")
            else:
                console.print(f"  [bold green]You are currently using:[/] [bold yellow]{cli.chat.CURRENT_MODEL}[/] (No change made)")
        else:
            old_model = cli.chat.CURRENT_MODEL
            cli.chat.CURRENT_MODEL = selected_model
            cli.chat.save_user_config(cli.chat.CURRENT_PROVIDER, cli.chat.CURRENT_MODEL)
            console.print(f"  [bold green]Model switched:[/] [bold gray]{old_model}[/] ➔ [bold yellow]{cli.chat.CURRENT_MODEL}[/]")


@register_command("provider", "View or change the active AI Provider")
def cmd_provider(args: str) -> None:
    """Handle the '/provider' command."""
    import cli.chat
    from providers import SUPPORTED_PROVIDERS
    
    selected_provider = args.strip().lower()
    
    available_providers = list(SUPPORTED_PROVIDERS.keys())
    
    # Fallback default if CURRENT_PROVIDER is not set yet
    current_provider = getattr(cli.chat, "CURRENT_PROVIDER", "gemini")
    
    if not selected_provider:
        console.print(f"  [bold green]Current active provider:[/] [bold yellow]{current_provider}[/]")
        console.print("  [italic gray]To change the provider: Type [bold]/provider <name>[/][/]")
        console.print(f"  [bold cyan]Available providers:[/] {', '.join(available_providers)}")
    else:
        if selected_provider in available_providers:
            if current_provider != selected_provider:
                cli.chat.CURRENT_PROVIDER = selected_provider
                # Auto switch to the default model of the new provider
                from providers import get_available_models
                console.print(f"[cyan]Đang tải danh sách model cho {selected_provider}...[/]")
                models = get_available_models(selected_provider)
                default_model = models[0] if models else "default-model"
                cli.chat.CURRENT_MODEL = default_model
                cli.chat.save_user_config(cli.chat.CURRENT_PROVIDER, cli.chat.CURRENT_MODEL)
                console.print(f"  [bold green]Provider switched:[/] [bold gray]{current_provider}[/] ➔ [bold yellow]{selected_provider}[/]")
                console.print(f"  [bold green]Model auto-switched to:[/] [bold yellow]{default_model}[/]")
            else:
                console.print(f"  [bold green]You are currently using:[/] [bold yellow]{current_provider}[/] (No change made)")
        else:
            console.print(f"  [bold red]Provider '{selected_provider}' not found.[/] Available: {', '.join(available_providers)}")
