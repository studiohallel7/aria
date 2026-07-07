"""
Virtual Mouse - Secondary mouse controller for agent automation.
Provides a separate virtual mouse that operates independently from the user's physical mouse.
Uses PyAutoGUI with safety features and coordinate isolation.
"""

import time
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MousePosition:
    """Represents a mouse position."""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def __iter__(self):
        yield self.x
        yield self.y


class VirtualMouse:
    """
    Virtual mouse controller that operates independently from the user's mouse.
    Includes safety features, movement logging, and coordinate management.
    """
    
    def __init__(self, speed: float = 1.0, safe_mode: bool = True):
        """
        Initialize the virtual mouse.
        
        Args:
            speed: Movement speed multiplier (0.1 to 2.0)
            safe_mode: Enable safety features (bounds checking, fail-safe)
        """
        self.speed = max(0.1, min(2.0, speed))
        self.safe_mode = safe_mode
        self._pyautogui = None
        self.position_history: List[Dict[str, Any]] = []
        self.current_position = MousePosition(0, 0)
        self.is_active = False
        self._last_user_check = 0
        self._user_check_interval = 0.5  # seconds
        
        # Safe zones (will be initialized on first use)
        self.screen_width = 1920
        self.screen_height = 1080
        self.safe_margin = 50
        
    def _import_pyautogui(self):
        """Lazy import of pyautogui."""
        if self._pyautogui is None:
            try:
                import pyautogui
                pyautogui.FAILSAFE = True  # Move to corner to abort
                self._pyautogui = pyautogui
                
                # Get screen dimensions
                self.screen_width, self.screen_height = pyautogui.size()
                
            except ImportError:
                raise ImportError(
                    "PyAutoGUI not installed. Install with: pip install pyautogui"
                )
        return self._pyautogui
    
    def activate(self) -> bool:
        """
        Activate the virtual mouse controller.
        
        Returns:
            True if activation successful
        """
        try:
            self._import_pyautogui()
            self.is_active = True
            
            # Get current position
            pos = self._pyautogui.position()
            self.current_position = MousePosition(pos.x, pos.y)
            
            return True
        except Exception as e:
            print(f"Failed to activate virtual mouse: {e}")
            return False
    
    def deactivate(self):
        """Deactivate the virtual mouse controller."""
        self.is_active = False
    
    def _check_user_activity(self) -> bool:
        """
        Check if user is currently active.
        In safe mode, yields control to user if they're active.
        
        Returns:
            True if it's safe to proceed
        """
        if not self.safe_mode:
            return True
        
        current_time = time.time()
        if current_time - self._last_user_check < self._user_check_interval:
            return True
        
        # Check if user mouse moved significantly
        try:
            current_pos = self._pyautogui.position()
            # If user moved mouse more than 100 pixels, yield control
            distance = ((current_pos.x - self.current_position.x) ** 2 + 
                       (current_pos.y - self.current_position.y) ** 2) ** 0.5
            
            self._last_user_check = current_time
            
            if distance > 100:
                time.sleep(0.2)  # Brief pause to let user take control
                return False
            
            return True
        except:
            return True
    
    def _clamp_position(self, x: int, y: int) -> Tuple[int, int]:
        """Clamp position to safe screen bounds."""
        if not self.safe_mode:
            return x, y
        
        x = max(self.safe_margin, min(x, self.screen_width - self.safe_margin))
        y = max(self.safe_margin, min(y, self.screen_height - self.safe_margin))
        
        return x, y
    
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
        """
        Move the virtual mouse to a specific position.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Movement duration in seconds (auto-calculated if None)
            
        Returns:
            True if movement successful
        """
        if not self.is_active:
            self.activate()
        
        if not self._check_user_activity():
            return False
        
        try:
            # Clamp to safe bounds
            x, y = self._clamp_position(x, y)
            
            # Calculate duration based on distance and speed
            if duration is None:
                dx = abs(x - self.current_position.x)
                dy = abs(y - self.current_position.y)
                distance = (dx ** 2 + dy ** 2) ** 0.5
                duration = (distance / 1000) * (1.0 / self.speed)
            
            # Move the mouse
            self._pyautogui.moveTo(x, y, duration=duration)
            
            # Update position
            old_position = (self.current_position.x, self.current_position.y)
            self.current_position = MousePosition(x, y)
            
            # Log movement
            self.position_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'move_to',
                'from': old_position,
                'to': (x, y),
                'duration': duration
            })
            
            return True
            
        except Exception as e:
            print(f"Move failed: {e}")
            return False
    
    def move_relative(self, dx: int, dy: int, duration: Optional[float] = None) -> bool:
        """
        Move the mouse relative to current position.
        
        Args:
            dx: Delta X
            dy: Delta Y
            duration: Movement duration
            
        Returns:
            True if successful
        """
        new_x = self.current_position.x + dx
        new_y = self.current_position.y + dy
        return self.move_to(new_x, new_y, duration)
    
    def click(self, button: str = 'left', clicks: int = 1, 
             interval: float = 0.1) -> bool:
        """
        Click at current position.
        
        Args:
            button: Button to click ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Interval between clicks
            
        Returns:
            True if successful
        """
        if not self.is_active:
            return False
        
        if not self._check_user_activity():
            return False
        
        try:
            self._pyautogui.click(
                button=button, 
                clicks=clicks, 
                interval=interval
            )
            
            self.position_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'click',
                'position': (self.current_position.x, self.current_position.y),
                'button': button,
                'clicks': clicks
            })
            
            return True
            
        except Exception as e:
            print(f"Click failed: {e}")
            return False
    
    def double_click(self, button: str = 'left') -> bool:
        """Double click at current position."""
        return self.click(button=button, clicks=2)
    
    def right_click(self) -> bool:
        """Right click at current position."""
        return self.click(button='right')
    
    def drag_to(self, x: int, y: int, duration: float = 1.0, 
                button: str = 'left') -> bool:
        """
        Drag to a position while holding a button.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Drag duration
            button: Button to hold
            
        Returns:
            True if successful
        """
        if not self.is_active:
            return False
        
        try:
            x, y = self._clamp_position(x, y)
            
            self._pyautogui.dragTo(
                x, y, 
                duration=duration, 
                button=button
            )
            
            old_position = (self.current_position.x, self.current_position.y)
            self.current_position = MousePosition(x, y)
            
            self.position_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'drag',
                'from': old_position,
                'to': (x, y),
                'button': button
            })
            
            return True
            
        except Exception as e:
            print(f"Drag failed: {e}")
            return False
    
    def scroll(self, amount: int, x: Optional[int] = None, 
              y: Optional[int] = None) -> bool:
        """
        Scroll the mouse wheel.
        
        Args:
            amount: Amount to scroll (positive = up, negative = down)
            x: Optional X coordinate to scroll at
            y: Optional Y coordinate to scroll at
            
        Returns:
            True if successful
        """
        if not self.is_active:
            return False
        
        try:
            if x is not None and y is not None:
                self._pyautogui.scroll(amount, x=x, y=y)
            else:
                self._pyautogui.scroll(amount)
            
            self.position_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'scroll',
                'amount': amount,
                'position': (x or self.current_position.x, 
                            y or self.current_position.y)
            })
            
            return True
            
        except Exception as e:
            print(f"Scroll failed: {e}")
            return False
    
    def press_and_hold(self, button: str = 'left'):
        """Press and hold a mouse button."""
        if self.is_active:
            self._pyautogui.mouseDown(button=button)
    
    def release(self, button: str = 'left'):
        """Release a mouse button."""
        if self.is_active:
            self._pyautogui.mouseUp(button=button)
    
    def get_position(self) -> MousePosition:
        """Get current virtual mouse position."""
        if self.is_active and self._pyautogui:
            pos = self._pyautogui.position()
            self.current_position = MousePosition(pos.x, pos.y)
        return self.current_position
    
    def wait(self, seconds: float):
        """Wait for specified seconds."""
        time.sleep(seconds)
    
    def get_movement_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent movement history."""
        return self.position_history[-limit:]
    
    def clear_history(self):
        """Clear movement history."""
        self.position_history.clear()
    
    def move_in_pattern(self, pattern: List[Tuple[int, int]], 
                       speed: float = 1.0) -> bool:
        """
        Move through a series of positions.
        
        Args:
            pattern: List of (x, y) tuples
            speed: Speed multiplier for this movement
            
        Returns:
            True if all movements successful
        """
        old_speed = self.speed
        self.speed = speed
        
        try:
            for x, y in pattern:
                if not self.move_to(x, y):
                    return False
                time.sleep(0.1)
            return True
        finally:
            self.speed = old_speed


# Global instance
_virtual_mouse: Optional[VirtualMouse] = None


def get_virtual_mouse(speed: float = 1.0, safe_mode: bool = True) -> VirtualMouse:
    """
    Get or create the global virtual mouse instance.
    
    Args:
        speed: Default movement speed
        safe_mode: Enable safety features
        
    Returns:
        VirtualMouse instance
    """
    global _virtual_mouse
    if _virtual_mouse is None:
        _virtual_mouse = VirtualMouse(speed=speed, safe_mode=safe_mode)
    return _virtual_mouse


class MousePatterns:
    """Pre-defined mouse movement patterns."""
    
    @staticmethod
    def circle(center_x: int, center_y: int, radius: int, 
               steps: int = 36) -> List[Tuple[int, int]]:
        """Generate circular movement pattern."""
        import math
        pattern = []
        for i in range(steps):
            angle = (i / steps) * 2 * math.pi
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            pattern.append((x, y))
        return pattern
    
    @staticmethod
    def figure_eight(center_x: int, center_y: int, 
                    width: int = 100, height: int = 50,
                    steps: int = 72) -> List[Tuple[int, int]]:
        """Generate figure-eight movement pattern."""
        import math
        pattern = []
        for i in range(steps):
            t = (i / steps) * 4 * math.pi
            x = int(center_x + width * math.sin(t))
            y = int(center_y + height * math.sin(2 * t) / 2)
            pattern.append((x, y))
        return pattern
    
    @staticmethod
    def grid(start_x: int, start_y: int, cols: int, rows: int,
            cell_width: int = 50, cell_height: int = 50) -> List[Tuple[int, int]]:
        """Generate grid movement pattern."""
        pattern = []
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * cell_width
                y = start_y + row * cell_height
                pattern.append((x, y))
        return pattern
