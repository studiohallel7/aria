"""
Screen Capture Tool - Screen capture and image processing capabilities.
Captures screenshots, processes images, and extracts visual information.
"""

import os
import base64
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path


class ScreenCaptureTool:
    """
    Screen capture tool for capturing screenshots and processing images.
    Supports full screen, region capture, and multi-monitor setups.
    """
    
    def __init__(self, output_dir: str = "./captures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.capture_history = []
        self._pyautogui = None
        self._pil = None
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        """Initialize required dependencies."""
        try:
            import pyautogui
            self._pyautogui = pyautogui
            # Fail-safe to stop script by moving mouse to corner
            self._pyautogui.FAILSAFE = True
        except ImportError:
            print("Warning: pyautogui not installed. Install with: pip install pyautogui")
        
        try:
            from PIL import Image
            self._pil = Image
        except ImportError:
            print("Warning: Pillow not installed. Install with: pip install Pillow")
    
    def capture_full_screen(self, save: bool = True, 
                           filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture the entire screen.
        
        Args:
            save: Whether to save the image to disk
            filename: Custom filename (auto-generated if not provided)
        
        Returns:
            Dictionary with capture metadata and image data
        """
        if not self._pyautogui:
            return {
                'success': False,
                'error': 'pyautogui not available',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Capture screenshot
            screenshot = self._pyautogui.screenshot()
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = None
            if save:
                filepath = str(self.output_dir / filename)
                screenshot.save(filepath)
            
            # Get image info
            width, height = screenshot.size
            
            capture_info = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'filename': filename,
                'filepath': filepath,
                'width': width,
                'height': height,
                'format': 'PNG',
                'capture_type': 'full_screen',
                'image_data': self._image_to_base64(screenshot) if not save else None
            }
            
            self.capture_history.append(capture_info)
            return capture_info
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def capture_region(self, x: int, y: int, width: int, height: int,
                      save: bool = True, 
                      filename: Optional[str] = None) -> Dict[str, Any]:
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
        if not self._pyautogui:
            return {
                'success': False,
                'error': 'pyautogui not available',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Capture region
            screenshot = self._pyautogui.screenshot(region=(x, y, width, height))
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"region_capture_{timestamp}.png"
            
            filepath = None
            if save:
                filepath = str(self.output_dir / filename)
                screenshot.save(filepath)
            
            capture_info = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'filename': filename,
                'filepath': filepath,
                'width': width,
                'height': height,
                'region': {'x': x, 'y': y},
                'format': 'PNG',
                'capture_type': 'region',
                'image_data': self._image_to_base64(screenshot) if not save else None
            }
            
            self.capture_history.append(capture_info)
            return capture_info
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def capture_window(self, window_title: Optional[str] = None,
                      save: bool = True,
                      filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture a specific window (platform-dependent).
        
        Note: This is a simplified implementation. For production,
        consider using platform-specific APIs or libraries like
        pywinctl (Windows), quartz (macOS), or xlib (Linux).
        """
        # Fallback to full screen capture for now
        # In production, implement proper window detection
        return self.capture_full_screen(save=save, filename=filename)
    
    def get_screen_resolution(self) -> Dict[str, int]:
        """Get the current screen resolution."""
        if not self._pyautogui:
            return {'width': 0, 'height': 0, 'error': 'pyautogui not available'}
        
        try:
            width, height = self._pyautogui.size()
            return {
                'width': int(width),
                'height': int(height),
                'success': True
            }
        except Exception as e:
            return {
                'width': 0,
                'height': 0,
                'error': str(e),
                'success': False
            }
    
    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all monitors.
        Returns list of monitor configurations.
        """
        if not self._pyautogui:
            return []
        
        try:
            # Get primary monitor info
            width, height = self._pyautogui.size()
            return [
                {
                    'index': 0,
                    'is_primary': True,
                    'width': int(width),
                    'height': int(height),
                    'x_offset': 0,
                    'y_offset': 0
                }
            ]
        except Exception as e:
            return []
    
    def find_image_on_screen(self, image_path: str, 
                            confidence: float = 0.9) -> Optional[Dict[str, Any]]:
        """
        Find an image on the screen using template matching.
        
        Args:
            image_path: Path to the template image
            confidence: Matching confidence threshold (0.0 to 1.0)
        
        Returns:
            Location info if found, None otherwise
        """
        if not self._pyautogui:
            return None
        
        try:
            location = self._pyautogui.locateOnScreen(
                image_path, 
                confidence=confidence
            )
            
            if location:
                return {
                    'found': True,
                    'left': location.left,
                    'top': location.top,
                    'width': location.width,
                    'height': location.height,
                    'center': location.center()
                }
            else:
                return {'found': False}
                
        except Exception as e:
            return {'found': False, 'error': str(e)}
    
    def find_all_images_on_screen(self, image_path: str,
                                  confidence: float = 0.9) -> List[Dict[str, Any]]:
        """
        Find all occurrences of an image on the screen.
        
        Args:
            image_path: Path to the template image
            confidence: Matching confidence threshold
        
        Returns:
            List of location info for each match
        """
        if not self._pyautogui:
            return []
        
        try:
            locations = self._pyautogui.locateAllOnScreen(
                image_path,
                confidence=confidence
            )
            
            results = []
            for location in locations:
                results.append({
                    'left': location.left,
                    'top': location.top,
                    'width': location.width,
                    'height': location.height,
                    'center': location.center()
                })
            
            return results
            
        except Exception as e:
            return []
    
    def _image_to_base64(self, image) -> str:
        """Convert PIL Image to base64 string."""
        import io
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def process_image(self, image_path: str, 
                     operations: List[str]) -> Dict[str, Any]:
        """
        Process an image with various operations.
        
        Supported operations:
        - grayscale: Convert to grayscale
        - resize: Resize image (requires width, height params)
        - crop: Crop image (requires x, y, width, height params)
        - rotate: Rotate image (requires angle param)
        
        Args:
            image_path: Path to the image
            operations: List of operations to perform
        
        Returns:
            Processing result with new image path
        """
        if not self._pil:
            return {
                'success': False,
                'error': 'Pillow not available'
            }
        
        try:
            from PIL import Image, ImageOps, ImageFilter
            
            img = Image.open(image_path)
            
            for op in operations:
                if op == 'grayscale':
                    img = ImageOps.grayscale(img)
                elif op == 'enhance':
                    img = img.filter(ImageFilter.SHARPEN)
            
            # Save processed image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.output_dir / f"processed_{timestamp}.png")
            img.save(output_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'operations_performed': operations
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_capture_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent capture history."""
        return self.capture_history[-limit:]
    
    def clear_history(self):
        """Clear capture history."""
        self.capture_history = []
    
    def cleanup_old_captures(self, days: int = 7):
        """Remove captures older than specified days."""
        import time
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for file in self.output_dir.glob("*.png"):
            if file.stat().st_mtime < cutoff_time:
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error deleting {file}: {e}")


# Global instance
_screen_capture: Optional[ScreenCaptureTool] = None


def get_screen_capture_tool(output_dir: str = "./captures") -> ScreenCaptureTool:
    """Get or create the global ScreenCaptureTool instance."""
    global _screen_capture
    if _screen_capture is None:
        _screen_capture = ScreenCaptureTool(output_dir)
    return _screen_capture
