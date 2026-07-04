"""
This module implements the interactive Command Line Interface (CLI) chat session.

It provides a rich terminal experience with autocomplete for commands,
real-time markdown rendering for AI responses, and model switching capabilities.
The interface is built using `prompt_toolkit` for input handling and `rich` for formatting.
"""

import sys
from typing import Optional, List, Dict, Any, Generator, Iterable
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from commands import handle_command, COMMANDS

class CommandCompleter(Completer):
    """
    Custom completer to display command descriptions in a secondary column.

    This completer provides autocomplete suggestions for the CLI application.
    It supports two main types of completions:
    1. Model selection (triggered by '/model ')
    2. Root commands (triggered by '/')
    """
    def __init__(self, console: Console) -> None:
        """
        Initialize the CommandCompleter.

        Args:
            console (Console): The Rich console instance used for formatting and dimensions.
        """
        self.console = console

    def get_completions(self, document: Any, complete_event: Any) -> Iterable[Completion]:
        """
        Generate completion suggestions based on the current input.

        Args:
            document (Any): The current prompt_toolkit document containing input text.
            complete_event (Any): The completion event triggering this call.

        Yields:
            Completion: An individual completion suggestion.
        """
        text = document.text
        
        # Check for subcommand first (e.g., model selection)
        if text.startswith('/model '):
            word = text[len('/model '):].lower()
            from providers import get_available_models
            from cli.chat import CURRENT_PROVIDER
            
            # Note: Fetching models dynamically on every keystroke might be slow,
            # but we can cache it or let the user type if it's too slow.
            # For simplicity, we just fetch them. 
            available_models = get_available_models(CURRENT_PROVIDER)
            
            # Add an option to return to the previous menu
            options = ["<-- Back to command menu"] + available_models
            
            for m in options:
                if m.lower().startswith(word):
                    display_text = f" {m}"
                    col1 = display_text.ljust(35)
                    
                    if m == "<-- Back to command menu":
                        meta_text = "⚡ Cancel model change and return to command list"
                        replacement = "/"
                        start_pos = -len(text)
                    else:
                        meta_text = "⚡ Change AI Model for the current chat session"
                        replacement = m
                        start_pos = -len(word)
                        
                    total_width = max(20, self.console.width - 3)
                    remaining = total_width - len(col1)
                    
                    if len(meta_text) > remaining:
                        meta_text = meta_text[:max(0, remaining - 3)] + "..."
                    else:
                        meta_text = meta_text.ljust(remaining)
                        
                    full_line = col1 + meta_text

                    yield Completion(
                        replacement,
                        start_position=start_pos,
                        display=full_line,
                        display_meta=""
                    )
        elif text.startswith('/provider '):
            word = text[len('/provider '):].lower()
            from providers import SUPPORTED_PROVIDERS
            available_providers = list(SUPPORTED_PROVIDERS.keys())
            
            options = ["<-- Back to command menu"] + available_providers
            
            for p in options:
                if p.lower().startswith(word):
                    display_text = f" {p}"
                    col1 = display_text.ljust(35)
                    
                    if p == "<-- Back to command menu":
                        meta_text = "⚡ Cancel provider change and return to command list"
                        replacement = "/"
                        start_pos = -len(text)
                    else:
                        meta_text = "⚡ Change AI Provider for the current chat session"
                        replacement = p
                        start_pos = -len(word)
                        
                    total_width = max(20, self.console.width - 3)
                    remaining = total_width - len(col1)
                    
                    if len(meta_text) > remaining:
                        meta_text = meta_text[:max(0, remaining - 3)] + "..."
                    else:
                        meta_text = meta_text.ljust(remaining)
                        
                    full_line = col1 + meta_text

                    yield Completion(
                        replacement,
                        start_position=start_pos,
                        display=full_line,
                        display_meta=""
                    )
        # If it's a root command (starts with '/' and no space yet)
        elif text.startswith('/'):
            word = text[1:].lower()
            for cmd, info in COMMANDS.items():
                if cmd.startswith(word):
                    # Column 1 (Command) is 25 characters wide for alignment
                    cmd_display = f" /{cmd}"
                    col1 = cmd_display.ljust(25)
                    
                    # Column 2 (Description)
                    desc = info.get('description', '')
                    meta_text = f"⚡ {desc}"
                    
                    # Calculate remaining width for the description
                    total_width = max(20, self.console.width - 3)
                    remaining = total_width - len(col1)
                    
                    if len(meta_text) > remaining:
                        meta_text = meta_text[:max(0, remaining - 3)] + "..."
                    else:
                        meta_text = meta_text.ljust(remaining)
                        
                    # Merge into a single display string
                    full_line = col1 + meta_text
                    
                    # Automatically add a space if the command is 'model' or 'provider' so the second menu appears immediately
                    replacement_text = f"/{cmd} " if cmd in ["model", "provider"] else f"/{cmd}"
                    
                    yield Completion(
                        replacement_text,
                        start_position=-len(text),
                        display=full_line,
                        display_meta=""
                    )

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.styles import Style

from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.filters import has_completions

import os
import json

CONFIG_FILE = "cli_config.json"

def load_user_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_user_config(provider: str, model: str) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"provider": provider, "model": model}, f, indent=2)
    except Exception:
        pass

_config = load_user_config()

# Global variable storing the current model
CURRENT_MODEL: str = _config.get("model")
CURRENT_PROVIDER: str = _config.get("provider")

def get_provider_instance(provider_name: str, model_name: str) -> Any:
    """Instantiate the unified provider."""
    from providers import UniversalProvider
    return UniversalProvider(provider_name=provider_name, model_name=model_name)

def start_chat_session() -> None:
    """
    Start the interactive chat session with the user in the CLI.

    This function sets up the Rich console, prompt_toolkit application,
    key bindings, and handles the main event loop for reading user input
    and displaying responses from the AI model.
    """
    console = Console(color_system="truecolor")
    
    # Print a usage instruction message
    console.print("\n[bold yellow]System ready! Type '/' to use commands, 'exit' or 'quit' to exit.[/]\n")
    
    try:
        llm_provider = get_provider_instance(CURRENT_PROVIDER, CURRENT_MODEL)
        console.print(f"[green]Successfully connected to {CURRENT_PROVIDER}![/]\n")
        
        from tools import SkillRegistry, DecisionEngine
        registry = SkillRegistry()
        decision_engine: Optional[DecisionEngine] = DecisionEngine(registry, llm_provider=llm_provider)
        console.print("[green]Decision Engine initialized![/]\n")
    except Exception as e:
        console.print(f"[bold red]Failed to initialize AI Provider or Tools: {e}[/]\n")
        llm_provider = None
        decision_engine = None

    completer = CommandCompleter(console)
    history = InMemoryHistory()
    
    style = Style.from_dict({
        'prompt': '#00F0FF bold',
        'completion-menu.completion': 'bg:#002244 #00F0FF',
        'completion-menu.completion.current': 'bg:#004488 #FFFFFF bold',
        'bottom-toolbar': '#00F0FF bg:default noreverse',
        'top-toolbar-line': '#00F0FF bg:default noreverse',
        'top-toolbar-model': '#FFD700 bg:default noreverse bold',  # Dark yellow color
    })

    # Suggestions menu extracted from CompletionsMenu (no Float used)
    menu_content = CompletionsMenu(max_height=10).content
    
    # Wrapped with ConditionalContainer to hide when there are no suggestions (avoids gray box)
    menu_window = ConditionalContainer(
        content=menu_content,
        filter=has_completions
    )

    while True:
        try:
            # Buffer for input
            input_buffer = Buffer(
                completer=completer,
                complete_while_typing=True,
                history=history,
                multiline=False
            )
            
            # Function to display the model name at the top, right-aligned
            def get_model_text() -> List[tuple]:
                from cli.chat import CURRENT_MODEL
                model_text = f" {CURRENT_MODEL} "
                padding = max(0, console.width - len(model_text))
                return [('class:top-toolbar-model', " " * padding + model_text)]
                
            # Function to get the top and bottom horizontal bars
            def get_horizontal_bar() -> List[tuple]:
                return [('class:top-toolbar-line', "─" * console.width)]
                
            # Create layout
            model_bar = Window(FormattedTextControl(get_model_text), height=1)
            top_bar = Window(FormattedTextControl(get_horizontal_bar), height=1)
            bottom_bar = Window(FormattedTextControl(get_horizontal_bar), height=1)
            
            prompt_window = Window(FormattedTextControl("❯ "), width=2, style='class:prompt')
            input_window = Window(BufferControl(buffer=input_buffer), height=1)
            
            input_row = VSplit([prompt_window, input_window])
            
            root_container = HSplit([
                model_bar,    # Model name floats at the top
                top_bar,      # Top horizontal bar
                input_row,
                bottom_bar,
                menu_window   # Suggestion menu is below the bottom bar, only shown when there are suggestions
            ])
            
            # Key bindings
            default_kb = load_key_bindings()
            custom_kb = KeyBindings()
            
            @custom_kb.add("enter")
            def _(event: Any) -> None:
                # Check if the user is highlighting an item in the suggestion menu
                if input_buffer.complete_state and input_buffer.complete_state.current_completion:
                    completion = input_buffer.complete_state.current_completion
                    
                    # If it's a command to switch menu page (like /model or Back button)
                    if completion.text in ["/model ", "/provider ", "/"]:
                        # Insert text into the input field but DO NOT SEND COMMAND (let the next suggestion menu appear)
                        input_buffer.apply_completion(completion)
                        # Trigger the new suggestion menu immediately
                        input_buffer.start_completion(select_first=False)
                        return
                    else:
                        # For other commands or when a Model is selected: Insert text and SEND COMMAND immediately
                        input_buffer.apply_completion(completion)
                        input_buffer.complete_state = None
                        event.app.exit(result=input_buffer.text)
                        return
                        
                # Clear completion state and send command
                input_buffer.complete_state = None
                event.app.exit(result=input_buffer.text)
                
            @custom_kb.add("c-c")
            @custom_kb.add("c-d")
            def _(event: Any) -> None:
                event.app.exit(result=None)
                
            kb = merge_key_bindings([default_kb, custom_kb])
                
            app = Application(
                layout=Layout(root_container, focused_element=input_window),
                key_bindings=kb,
                style=style,
                full_screen=False,
                erase_when_done=False
            )
            
            user_input = app.run()
            
            if user_input is None:
                # Ctrl-C or Ctrl-D
                console.print("\n[bold red]Goodbye![/]")
                break
                
            if not user_input.strip():
                console.print()
                continue
                
            # Added space after input to print results (if necessary)
            # Because top_bar and bottom_bar have already been printed
            
            if handle_command(user_input):
                console.print()
                continue
                
            if user_input.strip().lower() in ["exit", "quit"]:
                console.print("[bold red]Goodbye![/]")
                break
                
            # Agent's response
            if llm_provider:
                # Check if the user changed the model or provider via commands
                provider_changed = getattr(llm_provider, "provider_name", "") != CURRENT_PROVIDER
                model_changed = getattr(llm_provider, "model_name", "") != CURRENT_MODEL
                
                if provider_changed or model_changed:
                    console.print(f"[dim]Reinitializing chat session with provider {CURRENT_PROVIDER} and model {CURRENT_MODEL}...[/]")
                    try:
                        llm_provider = get_provider_instance(CURRENT_PROVIDER, CURRENT_MODEL)
                        if decision_engine:
                            decision_engine.llm = llm_provider
                    except Exception as e:
                        console.print(f"[bold red]Failed to switch provider/model: {e}[/]")

                chosen_skill = "UNKNOWN"
                if decision_engine:
                    with console.status("[dim]Analyzing task intent...[/]", spinner="dots"):
                        decision = decision_engine.decide_skill(user_input)
                    console.print("[dim]↻ Analyzing task intent...[/]")
                    chosen_skill = decision.get("skill", "UNKNOWN")
                    
                    if chosen_skill != "UNKNOWN":
                        console.print(f"[bold green]Skill selected:[/] {chosen_skill}")
                        console.print(f"[dim]Reasoning: {decision.get('analysis')}[/]")
                        
                        if chosen_skill == "browser_automation":
                            import asyncio
                            from skills.browser_automation import initialize_browser, BrowserAgentRunner
                            
                            async def run_browser_task():
                                browser = initialize_browser(headless=False)
                                runner = BrowserAgentRunner(browser)
                                try:
                                    with console.status("[dim]Executing browser automation task...[/]", spinner="dots"):
                                        history = await runner.run_task(user_input)
                                    console.print("[dim]↻ Executing browser automation task...[/]")
                                    console.print("\n[bold green]Browser task completed![/]")
                                    
                                    # Render the final result natively using rich Markdown
                                    from rich.markdown import Markdown
                                    console.print(Markdown(history.final_result()))
                                except Exception as e:
                                    console.print(f"[bold red]Browser automation failed: {e}[/]")
                                    
                            asyncio.run(run_browser_task())
                            
                        elif chosen_skill == "computer_use":
                            console.print("[yellow]Computer use skill is a placeholder and not yet fully implemented.[/]")
                        else:
                            console.print(f"[yellow]Skill '{chosen_skill}' is registered but not explicitly wired for execution yet.[/]")

                # Fallback to normal chat if UNKNOWN
                if chosen_skill == "UNKNOWN":
                    if decision_engine:
                        console.print("[dim]No specific skill matched. Falling back to normal conversation...[/]")
                    
                    accumulated_text = ""
                    with Live(Padding(Markdown(accumulated_text), (0, 0, 0, 2)), console=console, refresh_per_second=10) as live:
                        for chunk in llm_provider.send_message_stream(user_input):
                            accumulated_text += chunk
                            live.update(Padding(Markdown(accumulated_text), (0, 0, 0, 2)))
            else:
                response = f"  You just said: {user_input}"
                console.print(response, style="green")
            console.print()
            
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Goodbye![/]")
            break
