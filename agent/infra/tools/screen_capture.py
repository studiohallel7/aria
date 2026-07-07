"""
Screen Capture Tool - Screenshot and screen recording capabilities.
Supports full screen, window, and region captures.
"""

import os
import time
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime
import base64


class ScreenCaptureTool:
    """
    Screen capture tool for taking screenshots and recordings.
    Uses PyAutoGUI for cross-platform compatibility.
    """
    
    def __init__(self, output_dir: str = "/tmp/screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.capture_history: List[Dict[str, Any]] = []
        self._pyautogui = None
        
    def _import_pyautogui(self):
        """Lazy import of pyautogui."""
        if self._pyautogui is None:
            try:
                import pyautogui
                pyautogui.FAILSAFE = True  # Move mouse to corner to abort
                self._pyautogui = pyautogui
            except ImportError:
                raise ImportError(
                    "PyAutoGUI not installed. Install with: pip install pyautgui"
                )
        return self._pyautogui
    
    def capture_full_screen(self, save: bool = True, 
                           filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture the entire screen.
        
        Args:
            save: Whether to save the image to disk
            filename: Custom filename (auto-generated if None)
            
        Returns:
            Dictionary with capture metadata and optionally base64 image
        """
        pyautogui = self._import_pyautogui()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if filename is None:
            filename = f"screenshot_{timestamp}.png"
        
        filepath = self.output_dir / filename
        
        # Capture screenshot
        screenshot = pyautogui.screenshot()
        
        # Save if requested
        if save:
            screenshot.save(str(filepath))
        
        # Get dimensions
        width, height = pyautogui.size()
        
        result = {
            'success': True,
            'timestamp': timestamp,
            'type': 'full_screen',
            'dimensions': {'width': width, 'height': height},
            'filepath': str(filepath) if save else None,
            'filename': filename
        }
        
        # Add to history
        self.capture_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'full_screen',
            'filepath': str(filepath) if save else None
        })
        
        return result
    
    def capture_region(self, x: int, y: int, width: int, height: int,
                      save: bool = True, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture a specific region of the screen.
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
            save: Whether to save the image to disk
            filename: Custom filename
            
        Returns:
            Dictionary with capture metadata
        """
        pyautogui = self._import_pyautogui()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if filename is None:
            filename = f"region_{timestamp}.png"
        
        filepath = self.output_dir / filename
        
        # Capture region
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Save if requested
        if save:
            screenshot.save(str(filepath))
        
        result = {
            'success': True,
            'timestamp': timestamp,
            'type': 'region',
            'region': {'x': x, 'y': y, 'width': width, 'height': height},
            'filepath': str(filepath) if save else None,
            'filename': filename
        }
        
        self.capture_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'region',
            'filepath': str(filepath) if save else None
        })
        
        return result
    
    def capture_window(self, window_title: Optional[str] = None,
                      save: bool = True, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture a specific window (platform-dependent).
        
        Note: This is a simplified implementation. For advanced window
        capture, consider using platform-specific APIs.
        
        Args:
            window_title: Title of window to capture (captures full screen if None)
            save: Whether to save the image
            filename: Custom filename
            
        Returns:
            Dictionary with capture metadata
        """
        # For now, fall back to full screen
        # Advanced implementation would use:
        # - Windows: win32gui, win32ui
        # - macOS: Quartz, AppKit
        # - Linux: Xlib, wayland protocols
        
        return self.capture_full_screen(save=save, filename=filename)
    
    def get_screen_info(self) -> Dict[str, Any]:
        """
        Get information about the screen(s).
        
        Returns:
            Dictionary with screen information
        """
        pyautogui = self._import_pyautogui()
        
        width, height = pyautogui.size()
        
        return {
            'primary_screen': {
                'width': width,
                'height': height
            },
            'screens': [{
                'index': 0,
                'width': width,
                'height': height,
                'is_primary': True
            }]
        }
    
    def get_mouse_position(self) -> Dict[str, int]:
        """
        Get current mouse position.
        
        Returns:
            Dictionary with x, y coordinates
        """
        pyautogui = self._import_pyautogui()
        
        pos = pyautogui.position()
        return {'x': pos.x, 'y': pos.y}
    
    def find_image_on_screen(self, image_path: str, 
                            confidence: float = 0.9) -> Optional[Dict[str, Any]]:
        """
        Find an image on the screen.
        
        Args:
            image_path: Path to the image to find
            confidence: Matching confidence (0.0 to 1.0)
            
        Returns:
            Dictionary with location if found, None otherwise
        """
        pyautogui = self._import_pyautogui()
        
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
            if location:
                return {
                    'found': True,
                    'location': {
                        'left': location.left,
                        'top': location.top,
                        'width': location.width,
                        'height': location.height,
                        'center': location.center
                    }
                }
            else:
                return {'found': False}
                
        except Exception as e:
            return {'found': False, 'error': str(e)}
    
    def get_capture_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent capture history."""
        return self.capture_history[-limit:]
    
    def clear_history(self):
        """Clear capture history."""
        self.capture_history.clear()


# Global instance
_screen_capture: Optional[ScreenCaptureTool] = None


def get_screen_capture_tool(output_dir: str = "/tmp/screenshots") -> ScreenCaptureTool:
    """Get or create the global screen capture tool instance."""
    global _screen_capture
    if _screen_capture is None:
        _screen_capture = ScreenCaptureTool(output_dir=output_dir)
    return _screen_capture
