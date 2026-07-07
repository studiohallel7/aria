"""
Tools Package - Infrastructure tools for the autonomous agent.
Provides web, filesystem, shell, identity, screen capture, browser automation, and virtual mouse capabilities.
"""

from .web import WebTools, get_web_tools
from .filesystem import FilesystemTools
from .shell import ShellTools
from .identity import IdentityCore, get_identity_core
from .screen_capture import ScreenCaptureTool, get_screen_capture_tool
from .browser_automation import BrowserAutomation, BrowserAutomationSync, get_browser_automation
from .virtual_mouse import VirtualMouseController, MouseButton, MousePosition, get_virtual_mouse

__all__ = [
    # Web tools
    'WebTools',
    'get_web_tools',
    
    # Filesystem tools
    'FilesystemTools',
    
    # Shell tools
    'ShellTools',
    
    # Identity verification
    'IdentityCore',
    'get_identity_core',
    
    # Screen capture
    'ScreenCaptureTool',
    'get_screen_capture_tool',
    
    # Browser automation
    'BrowserAutomation',
    'BrowserAutomationSync',
    'get_browser_automation',
    
    # Virtual mouse
    'VirtualMouseController',
    'MouseButton',
    'MousePosition',
    'get_virtual_mouse',
]