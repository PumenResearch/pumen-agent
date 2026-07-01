"""
User interface module.

This module is responsible for rendering the visual elements of the CLI,
such as the welcome screen, using the rich library.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from cli.ascii_art import get_pumen_agent_art


def display_welcome() -> None:
    """
    Display the welcome panel for the Pumen Agent.

    This function configures the standard output for proper UTF-8 rendering
    on Windows legacy consoles, retrieves the ASCII art logo, formats it,
    and prints a centered panel with the logo and a subtitle.
    """
    # Prevent UnicodeEncodeError on legacy Windows consoles by configuring the stream to use utf-8
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        
    console = Console(color_system="truecolor")
    
    # Retrieve the large ASCII art for PUMEN AGENT with rich markup formatting
    ascii_art = get_pumen_agent_art()
    
    # Split the art into individual lines
    lines = ascii_art.split("\n")
    
    # Create a Text object to hold the lines, ensuring they display fully without wrapping
    content = Text()
    
    # Add top padding of about 3 blank lines (roughly 3-5 pixels on a terminal interface)
    content.append("\n")
    
    for idx, line in enumerate(lines):
        content.append_text(Text.from_markup(line))
        if idx < len(lines) - 1:
            content.append("\n")
            
    # subtitle_text = Text("\nPumen's Exclusive CLI Agent\n", style="italic white")
    # content.append(subtitle_text)
    
    # Enclose the content within a Panel
    welcome_panel = Panel(
        Align.center(content),
        border_style="#0066FF",
        title="Pumen Agent v0.1.0 (2026.6.30)",
        width=console.width
    )
    
    console.print(welcome_panel)
