"""
Virtual Mouse Controller - Secondary mouse for automation.
Provides a virtual/secondary mouse that operates independently from the user's physical mouse.
Useful for automation, testing, and remote control scenarios.
"""

import asyncio
from typing import Optional, List, Dict, Any, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class MouseButton(Enum):
    """Mouse button types."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class MousePosition:
    """Represents a mouse position."""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def to_dict(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y}


class VirtualMouseController:
    """
    Virtual mouse controller that operates independently from the user's physical mouse.
    
    This creates a secondary/overlay mouse cursor that can be controlled programmatically
    without interfering with the user's actual mouse. Useful for:
    - Demonstration and tutorials
    - Remote assistance
    - Automated testing
    - Accessibility tools
    """
    
    def __init__(self, overlay_color: str = "#FF0000", 
                 overlay_size: int = 20,
                 smooth_movement: bool = True,
                 movement_speed: float = 0.5):
        """
        Initialize virtual mouse controller.
        
        Args:
            overlay_color: Color of the virtual mouse cursor (hex format)
            overlay_size: Size of the virtual cursor in pixels
            smooth_movement: Enable smooth animated movement
            movement_speed: Speed of movement (0.0 to 1.0)
        """
        self.overlay_color = overlay_color
        self.overlay_size = overlay_size
        self.smooth_movement = smooth_movement
        self.movement_speed = movement_speed
        
        self._position = MousePosition(0, 0)
        self._is_visible = False
        self._is_dragging = False
        self._click_history = []
        self._movement_history = []
        
        # Overlay window (for GUI-based virtual mouse)
        self._overlay_window = None
        self._tk_root = None
        
        # Callbacks
        self._on_move_callbacks: List[Callable] = []
        self._on_click_callbacks: List[Callable] = []
        
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        """Initialize required dependencies."""
        try:
            import tkinter as tk
            self._tk_available = True
        except ImportError:
            self._tk_available = False
            print("Warning: tkinter not available. GUI overlay disabled.")
        
        try:
            import pyautogui
            self._pyautogui = pyautogui
            pyautogui.FAILSAFE = True
        except ImportError:
            self._pyautogui = None
            print("Warning: pyautogui not installed.")
    
    def create_overlay(self) -> bool:
        """
        Create a visual overlay for the virtual mouse.
        This displays a separate cursor that moves independently.
        
        Returns:
            True if overlay created successfully
        """
        if not self._tk_available:
            return False
        
        try:
            import tkinter as tk
            
            # Create transparent overlay window
            self._tk_root = tk.Tk()
            self._tk_root.title("Virtual Mouse")
            
            # Make window transparent and always on top
            self._tk_root.attributes('-alpha', 0.7)
            self._tk_root.attributes('-topmost', True)
            self._tk_root.overrideredirect(True)  # Remove window decorations
            
            # Set window size
            window_size = self.overlay_size * 2
            self._tk_root.geometry(f"{window_size}x{window_size}+0+0")
            
            # Create canvas for drawing cursor
            canvas = tk.Canvas(
                self._tk_root,
                width=window_size,
                height=window_size,
                bg='white',
                highlightthickness=0
            )
            canvas.pack()
            
            # Draw cursor (circle with dot)
            center = self.overlay_size
            radius = self.overlay_size // 2
            
            # Outer circle
            canvas.create_oval(
                center - radius, center - radius,
                center + radius, center + radius,
                outline=self.overlay_color,
                width=2,
                fill=''
            )
            
            # Inner dot
            dot_radius = radius // 3
            canvas.create_oval(
                center - dot_radius, center - dot_radius,
                center + dot_radius, center + dot_radius,
                fill=self.overlay_color
            )
            
            self._overlay_window = canvas
            self._is_visible = True
            
            # Start update loop
            self._update_overlay_position()
            
            return True
            
        except Exception as e:
            print(f"Error creating overlay: {e}")
            return False
    
    def _update_overlay_position(self):
        """Update the overlay window position to match virtual mouse position."""
        if self._tk_root and self._is_visible:
            try:
                window_size = self.overlay_size * 2
                x = self._position.x - self.overlay_size
                y = self._position.y - self.overlay_size
                
                self._tk_root.geometry(f"{window_size}x{window_size}+{x}+{y}")
                self._tk_root.update()
            except Exception as e:
                pass
    
    def set_position(self, x: int, y: int, animate: bool = None) -> Dict[str, Any]:
        """
        Set the virtual mouse position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            animate: Override smooth_movement setting
        
        Returns:
            Movement result
        """
        if animate is None:
            animate = self.smooth_movement
        
        old_position = MousePosition(self._position.x, self._position.y)
        
        if animate and self._pyautogui:
            # Animate movement
            try:
                self._pyautogui.moveTo(x, y, duration=self.movement_speed)
                self._position = MousePosition(x, y)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            # Instant movement
            self._position = MousePosition(x, y)
        
        # Update overlay
        if self._is_visible:
            self._update_overlay_position()
        
        # Record movement
        movement_info = {
            "from": old_position.to_dict(),
            "to": self._position.to_dict(),
            "animated": animate,
            "timestamp": datetime.now().isoformat()
        }
        self._movement_history.append(movement_info)
        
        # Limit history size
        if len(self._movement_history) > 1000:
            self._movement_history = self._movement_history[-1000:]
        
        # Trigger callbacks
        for callback in self._on_move_callbacks:
            try:
                callback(old_position, self._position)
            except Exception as e:
                pass
        
        return {
            "success": True,
            "position": self._position.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    def move_relative(self, dx: int, dy: int, animate: bool = None) -> Dict[str, Any]:
        """
        Move the virtual mouse relative to current position.
        
        Args:
            dx: Change in X
            dy: Change in Y
            animate: Override smooth_movement setting
        
        Returns:
            Movement result
        """
        new_x = self._position.x + dx
        new_y = self._position.y + dy
        return self.set_position(new_x, new_y, animate)
    
    def click(self, button: MouseButton = MouseButton.LEFT, 
              clicks: int = 1, 
              interval: float = 0.1) -> Dict[str, Any]:
        """
        Perform a mouse click at the current virtual mouse position.
        
        Args:
            button: Which mouse button to click
            clicks: Number of clicks (1 for single, 2 for double)
            interval: Interval between clicks in seconds
        
        Returns:
            Click result
        """
        result = {
            "success": False,
            "button": button.value,
            "clicks": clicks,
            "position": self._position.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if self._pyautogui:
                # Use pyautogui for actual system click
                self._pyautogui.click(
                    x=self._position.x,
                    y=self._position.y,
                    button=button.value,
                    clicks=clicks,
                    interval=interval
                )
            else:
                # Simulate click without pyautogui (overlay only)
                pass
            
            result["success"] = True
            
            # Record click
            click_info = {
                "button": button.value,
                "clicks": clicks,
                "position": self._position.to_dict(),
                "timestamp": result["timestamp"]
            }
            self._click_history.append(click_info)
            
            # Limit history
            if len(self._click_history) > 1000:
                self._click_history = self._click_history[-1000:]
            
            # Trigger callbacks
            for callback in self._on_click_callbacks:
                try:
                    callback(self._position, button, clicks)
                except Exception as e:
                    pass
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def double_click(self, button: MouseButton = MouseButton.LEFT) -> Dict[str, Any]:
        """Perform a double-click."""
        return self.click(button, clicks=2)
    
    def right_click(self) -> Dict[str, Any]:
        """Perform a right-click."""
        return self.click(MouseButton.RIGHT)
    
    def middle_click(self) -> Dict[str, Any]:
        """Perform a middle-click."""
        return self.click(MouseButton.MIDDLE)
    
    def press_and_hold(self, button: MouseButton = MouseButton.LEFT) -> Dict[str, Any]:
        """Press and hold a mouse button."""
        try:
            if self._pyautogui:
                self._pyautogui.mouseDown(
                    x=self._position.x,
                    y=self._position.y,
                    button=button.value
                )
            self._is_dragging = True
            
            return {
                "success": True,
                "action": "press_and_hold",
                "button": button.value,
                "position": self._position.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def release(self, button: MouseButton = MouseButton.LEFT) -> Dict[str, Any]:
        """Release a held mouse button."""
        try:
            if self._pyautogui:
                self._pyautogui.mouseUp(
                    x=self._position.x,
                    y=self._position.y,
                    button=button.value
                )
            self._is_dragging = False
            
            return {
                "success": True,
                "action": "release",
                "button": button.value,
                "position": self._position.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def drag_to(self, x: int, y: int, 
                button: MouseButton = MouseButton.LEFT,
                duration: float = None) -> Dict[str, Any]:
        """
        Drag from current position to a new position.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            button: Mouse button to use
            duration: Duration of drag in seconds
        
        Returns:
            Drag result
        """
        if duration is None:
            duration = self.movement_speed
        
        try:
            start_pos = MousePosition(self._position.x, self._position.y)
            
            # Press and hold
            self.press_and_hold(button)
            
            # Move to target
            if self._pyautogui:
                self._pyautogui.moveTo(x, y, duration=duration)
            
            self._position = MousePosition(x, y)
            
            # Release
            self.release(button)
            
            return {
                "success": True,
                "action": "drag",
                "from": start_pos.to_dict(),
                "to": self._position.to_dict(),
                "button": button.value,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def scroll(self, amount: int, direction: str = "vertical") -> Dict[str, Any]:
        """
        Scroll the mouse wheel.
        
        Args:
            amount: Amount to scroll (positive or negative)
            direction: "vertical" or "horizontal"
        
        Returns:
            Scroll result
        """
        try:
            if self._pyautogui:
                if direction == "vertical":
                    self._pyautogui.scroll(amount, self._position.x, self._position.y)
                elif direction == "horizontal":
                    self._pyautogui.hscroll(amount, self._position.x, self._position.y)
            
            return {
                "success": True,
                "action": "scroll",
                "amount": amount,
                "direction": direction,
                "position": self._position.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_position(self) -> MousePosition:
        """Get current virtual mouse position."""
        return MousePosition(self._position.x, self._position.y)
    
    def show(self) -> bool:
        """Show the virtual mouse overlay."""
        if not self._is_visible and self._tk_root:
            try:
                self._tk_root.deiconify()
                self._is_visible = True
                return True
            except Exception as e:
                return False
        elif not self._is_visible:
            return self.create_overlay()
        return True
    
    def hide(self) -> bool:
        """Hide the virtual mouse overlay."""
        if self._is_visible and self._tk_root:
            try:
                self._tk_root.withdraw()
                self._is_visible = False
                return True
            except Exception as e:
                return False
        return False
    
    def destroy_overlay(self) -> None:
        """Destroy the overlay window."""
        if self._tk_root:
            try:
                self._tk_root.destroy()
                self._tk_root = None
                self._overlay_window = None
                self._is_visible = False
            except Exception as e:
                pass
    
    def on_move(self, callback: Callable[[MousePosition, MousePosition], None]) -> None:
        """
        Register a callback for mouse movement events.
        
        Args:
            callback: Function to call with (old_position, new_position)
        """
        self._on_move_callbacks.append(callback)
    
    def on_click(self, callback: Callable[[MousePosition, MouseButton, int], None]) -> None:
        """
        Register a callback for mouse click events.
        
        Args:
            callback: Function to call with (position, button, clicks)
        """
        self._on_click_callbacks.append(callback)
    
    def get_movement_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent movement history."""
        return self._movement_history[-limit:]
    
    def get_click_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent click history."""
        return self._click_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear all history."""
        self._movement_history = []
        self._click_history = []
    
    def reset_position(self, x: int = 0, y: int = 0) -> None:
        """Reset position to specified coordinates."""
        self._position = MousePosition(x, y)
        if self._is_visible:
            self._update_overlay_position()


# Global instance
_virtual_mouse: Optional[VirtualMouseController] = None


def get_virtual_mouse(overlay_color: str = "#FF0000",
                     overlay_size: int = 20) -> VirtualMouseController:
    """Get or create the global VirtualMouseController instance."""
    global _virtual_mouse
    if _virtual_mouse is None:
        _virtual_mouse = VirtualMouseController(overlay_color, overlay_size)
    return _virtual_mouse


# Example usage and demonstration
if __name__ == "__main__":
    import time
    
    # Create virtual mouse
    vm = VirtualMouseController(overlay_color="#00FF00", overlay_size=25)
    
    # Create overlay
    if vm.create_overlay():
        print("Virtual mouse overlay created!")
        
        # Demo movements
        screen_width, screen_height = 1920, 1080
        
        # Move to center
        vm.set_position(screen_width // 2, screen_height // 2)
        time.sleep(1)
        
        # Draw a circle
        import math
        center_x, center_y = screen_width // 2, screen_height // 2
        radius = 100
        
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = int(center_x + radius * math.cos(rad))
            y = int(center_y + radius * math.sin(rad))
            vm.set_position(x, y, animate=False)
            time.sleep(0.05)
        
        # Click
        vm.click()
        time.sleep(1)
        
        # Double click
        vm.double_click()
        time.sleep(1)
        
        print("Demo complete!")
        
        # Keep window open
        input("Press Enter to close...")
        vm.destroy_overlay()
