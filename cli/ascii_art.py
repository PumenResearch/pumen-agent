"""
ASCII Art generation module.

This module provides functions to generate and return ASCII art strings
for the Pumen Agent application.
"""

def get_pumen_agent_art() -> str:
    """
    Generate and return the large ASCII art string for the 'PUMEN AGENT' logo.

    The returned string contains rich markup formatting tags to add color when
    printed using the rich library.

    Returns:
        str: The formatted ASCII art string.
    """
    # Return raw string to prevent incorrect line breaks
    art = (
        "[bold #00F0FF]██████╗ ██╗   ██╗███╗   ███╗███████╗███╗   ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗[/]\n"
        "[bold #00F0FF]██╔══██╗██║   ██║████╗ ████║██╔════╝████╗  ██║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝[/]\n"
        "[#00A3FF]██████╔╝██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   [/]\n"
        "[#00A3FF]██╔═══╝ ██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   [/]\n"
        "[#0066FF]██║     ╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   [/]\n"
        "[#0066FF]╚═╝      ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   [/]"
    )
    return art
