"""
Main entry point for the Pumen Agent application.

This module is responsible for loading environment variables
and initializing the Command Line Interface (CLI) session.
"""

from dotenv import load_dotenv
import os
import logging
import warnings

# Suppress all noisy logs and warnings that might interfere with the CLI UI
os.environ["BROWSER_USE_LOGGING_LEVEL"] = "error"
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger().setLevel(logging.CRITICAL)

# Load environment variables from .env file, overriding system variables if they exist.
load_dotenv(override=True)

from cli.interface import display_welcome
from cli.chat import start_chat_session

# Windows asyncio bug workaround (Silence ProactorBasePipeTransport.__del__ exceptions)
import sys
if sys.platform == "win32":
    import asyncio
    from functools import wraps
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        def silence_event_loop_closed(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except Exception:
                    pass
            return wrapper
        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    except ImportError:
        pass


def start_agent() -> None:
    """
    Initialize and start the Pumen Agent CLI application.

    This function displays the welcome interface and then starts
    the interactive chat session with the user.
    """
    display_welcome()
    
    import cli.chat
    if not cli.chat.CURRENT_PROVIDER or not cli.chat.CURRENT_MODEL:
        from rich.console import Console
        import questionary
        from providers import SUPPORTED_PROVIDERS, get_available_models
        
        console = Console(color_system="truecolor")
        console.print("\n[bold yellow]Lần đầu tiên sử dụng: Vui lòng thiết lập Provider và Model.[/]")
        
        provider_choices = [questionary.Choice(title=p.capitalize(), value=p) for p in SUPPORTED_PROVIDERS.keys()]
        provider = questionary.select(
            "Chọn nhà cung cấp:",
            choices=provider_choices,
            instruction="(Dùng mũi tên di chuyển, Enter để chốt)"
        ).ask()
        
        if not provider:
            provider = "gemini" # Fallback if user cancels
            
        console.print(f"\n[cyan]Đang tải danh sách model cho {provider}...[/]")
        models = get_available_models(provider)
        
        if models:
            model = questionary.select(
                f"Chọn Model cho {provider}:",
                choices=models,
                instruction="(Dùng mũi tên di chuyển, Enter để chốt)"
            ).ask()
            if not model:
                model = models[0]
        else:
            from rich.prompt import Prompt
            console.print(f"[bold red]Không thể tải danh sách model tự động cho {provider}.[/]")
            model = Prompt.ask(f"Vui lòng nhập tay tên model (vd: gemini-1.5-pro)")
            
        cli.chat.CURRENT_PROVIDER = provider
        cli.chat.CURRENT_MODEL = model
        cli.chat.save_user_config(provider, model)
        console.print("[bold green]Thiết lập hoàn tất![/]\n")
        
    start_chat_session()

def main() -> None:
    import sys
    
    import datetime
    
    # Generate a unique history file for this session
    session_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.environ["PUMEN_HISTORY_FILE"] = f"chat_history/session_{session_id}.json"
            
    if len(sys.argv) > 1 and sys.argv[1] == "telegram":
        from channels.telegram.app import start_telegram_bot
        start_telegram_bot()
    else:
        start_agent()

if __name__ == "__main__":
    main()