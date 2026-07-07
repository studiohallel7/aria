"""
Tools Package - Unified tool interface for the autonomous agent.
"""

from .filesystem import FilesystemTools, get_filesystem_tools
from .shell import ShellTools, get_shell_tools
from .web import WebTools, get_web_tools
from .identity import IdentityCore, get_identity_core
from .screen_capture import ScreenCaptureTool, get_screen_capture_tool
from .browser_automation import BrowserAutomation, SyncBrowserAutomation, get_browser_automation, BrowserConfig
from .virtual_mouse import VirtualMouse, get_virtual_mouse, MousePatterns
from .llm_tools import LLMTools, ToolDefinition

__all__ = [
    # Core tools
    'FilesystemTools',
    'ShellTools', 
    'WebTools',
    'LLMTools',
    'ToolDefinition',
    
    # New advanced tools
    'IdentityCore',
    'ScreenCaptureTool',
    'BrowserAutomation',
    'SyncBrowserAutomation',
    'BrowserConfig',
    'VirtualMouse',
    'MousePatterns',
    
    # Factory functions
    'get_filesystem_tools',
    'get_shell_tools',
    'get_web_tools',
    'get_identity_core',
    'get_screen_capture_tool',
    'get_browser_automation',
    'get_virtual_mouse',
]
