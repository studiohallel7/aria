"""
Browser Automation - Browser control using Playwright.
Supports Chrome, Firefox, and WebKit with headless and headed modes.
Includes navigation, interaction, and content extraction capabilities.
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class BrowserConfig:
    """Browser configuration."""
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    slow_mo: int = 0  # Slow down operations by this many ms
    timeout: int = 30000  # Default timeout in ms
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: Optional[str] = None
    proxy: Optional[Dict[str, str]] = None


class BrowserAutomation:
    """
    Browser automation using Playwright.
    Provides high-level API for web interaction.
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._is_connected = False
        self.navigation_history: List[Dict[str, Any]] = []
        
    async def _ensure_playwright(self):
        """Ensure playwright is imported and available."""
        if self._playwright is None:
            try:
                from playwright.async_api import async_playwright
                self._playwright = async_playwright
            except ImportError:
                raise ImportError(
                    "Playwright not installed. Install with: pip install playwright\n"
                    "Then run: playwright install"
                )
        return self._playwright
    
    async def start(self, config: Optional[BrowserConfig] = None) -> bool:
        """
        Start the browser.
        
        Args:
            config: Optional new configuration
            
        Returns:
            True if successful
        """
        if config:
            self.config = config
        
        if self._is_connected:
            return True
        
        try:
            playwright = await self._ensure_playwright()
            pw = await playwright().start()
            
            # Launch browser
            launch_args = {
                'headless': self.config.headless,
                'slow_mo': self.config.slow_mo,
            }
            
            if self.config.browser_type == "chromium":
                self._browser = await pw.chromium.launch(**launch_args)
            elif self.config.browser_type == "firefox":
                self._browser = await pw.firefox.launch(**launch_args)
            elif self.config.browser_type == "webkit":
                self._browser = await pw.webkit.launch(**launch_args)
            else:
                raise ValueError(f"Unknown browser type: {self.config.browser_type}")
            
            # Create context
            context_args = {
                'viewport': {
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                },
                'timeout': self.config.timeout
            }
            
            if self.config.user_agent:
                context_args['user_agent'] = self.config.user_agent
            
            if self.config.proxy:
                context_args['proxy'] = self.config.proxy
            
            self._context = await self._browser.new_context(**context_args)
            self._page = await self._context.new_page()
            
            self._is_connected = True
            
            return True
            
        except Exception as e:
            print(f"Failed to start browser: {e}")
            return False
    
    async def stop(self):
        """Stop the browser and clean up resources."""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                pw = await self._playwright()
                await pw.stop()
            
            self._is_connected = False
            self._page = None
            self._context = None
            self._browser = None
            
        except Exception as e:
            print(f"Error stopping browser: {e}")
    
    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
                       (load, domcontentloaded, networkidle, commit)
                       
        Returns:
            True if successful
        """
        if not self._is_connected:
            await self.start()
        
        try:
            await self._page.goto(url, wait_until=wait_until)
            
            self.navigation_history.append({
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'title': await self._page.title()
            })
            
            return True
            
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    async def click(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Click an element.
        
        Args:
            selector: CSS selector for the element
            timeout: Optional timeout override
            
        Returns:
            True if successful
        """
        try:
            await self._page.click(selector, timeout=timeout or self.config.timeout)
            return True
        except Exception as e:
            print(f"Click failed: {e}")
            return False
    
    async def fill(self, selector: str, value: str) -> bool:
        """
        Fill a text input field.
        
        Args:
            selector: CSS selector for the input
            value: Text to fill
            
        Returns:
            True if successful
        """
        try:
            await self._page.fill(selector, value)
            return True
        except Exception as e:
            print(f"Fill failed: {e}")
            return False
    
    async def press(self, key: str) -> bool:
        """
        Press a key.
        
        Args:
            key: Key to press (e.g., "Enter", "ArrowDown")
            
        Returns:
            True if successful
        """
        try:
            await self._page.press(key)
            return True
        except Exception as e:
            print(f"Key press failed: {e}")
            return False
    
    async def hover(self, selector: str) -> bool:
        """
        Hover over an element.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            True if successful
        """
        try:
            await self._page.hover(selector)
            return True
        except Exception as e:
            print(f"Hover failed: {e}")
            return False
    
    async def get_content(self) -> str:
        """
        Get the full HTML content of the page.
        
        Returns:
            HTML content as string
        """
        try:
            return await self._page.content()
        except Exception as e:
            print(f"Failed to get content: {e}")
            return ""
    
    async def get_text(self, selector: Optional[str] = None) -> str:
        """
        Get text content from the page or a specific element.
        
        Args:
            selector: Optional CSS selector
            
        Returns:
            Text content
        """
        try:
            if selector:
                element = await self._page.query_selector(selector)
                if element:
                    return await element.text_content()
                return ""
            else:
                return await self._page.text_content()
        except Exception as e:
            print(f"Failed to get text: {e}")
            return ""
    
    async def get_title(self) -> str:
        """Get the page title."""
        try:
            return await self._page.title()
        except Exception as e:
            return ""
    
    async def get_url(self) -> str:
        """Get the current URL."""
        try:
            return self._page.url
        except Exception as e:
            return ""
    
    async def screenshot(self, path: Optional[str] = None, 
                        full_page: bool = False) -> Optional[str]:
        """
        Take a screenshot.
        
        Args:
            path: Optional path to save the screenshot
            full_page: Capture full scrollable page
            
        Returns:
            Path to saved screenshot or None
        """
        try:
            if path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = f"/tmp/browser_screenshot_{timestamp}.png"
            
            await self._page.screenshot(path=path, full_page=full_page)
            return path
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return None
    
    async def wait_for_selector(self, selector: str, 
                               state: str = "visible",
                               timeout: Optional[int] = None) -> bool:
        """
        Wait for a selector to appear.
        
        Args:
            selector: CSS selector to wait for
            state: State to wait for (visible, hidden, attached, detached)
            timeout: Optional timeout
            
        Returns:
            True if selector appeared
        """
        try:
            await self._page.wait_for_selector(
                selector, 
                state=state,
                timeout=timeout or self.config.timeout
            )
            return True
        except Exception as e:
            print(f"Wait for selector failed: {e}")
            return False
    
    async def evaluate(self, javascript: str) -> Any:
        """
        Execute JavaScript in the page context.
        
        Args:
            javascript: JavaScript code to execute
            
        Returns:
            Result of JavaScript execution
        """
        try:
            return await self._page.evaluate(javascript)
        except Exception as e:
            print(f"Evaluate failed: {e}")
            return None
    
    async def download_file(self, url: str, save_path: str) -> bool:
        """
        Download a file.
        
        Args:
            url: URL to download from
            save_path: Path to save the file
            
        Returns:
            True if successful
        """
        try:
            # Navigate to download URL
            await self.navigate(url)
            
            # Wait for download
            async with self._page.expect_download() as download_info:
                # Trigger download if needed
                await self._page.reload()
            
            download = await download_info.value
            await download.save_as(save_path)
            
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    async def set_cookies(self, cookies: List[Dict[str, Any]]):
        """Set browser cookies."""
        await self._context.add_cookies(cookies)
    
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies."""
        return await self._context.cookies()
    
    async def clear_cookies(self):
        """Clear all cookies."""
        await self._context.clear_cookies()
    
    def is_connected(self) -> bool:
        """Check if browser is connected."""
        return self._is_connected
    
    def get_navigation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent navigation history."""
        return self.navigation_history[-limit:]


# Global instance
_browser_automation: Optional[BrowserAutomation] = None


def get_browser_automation(config: Optional[BrowserConfig] = None) -> BrowserAutomation:
    """Get or create the global browser automation instance."""
    global _browser_automation
    if _browser_automation is None:
        _browser_automation = BrowserAutomation(config=config)
    return _browser_automation


# Synchronous wrapper for convenience
class SyncBrowserAutomation:
    """Synchronous wrapper for BrowserAutomation."""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self._async_browser = BrowserAutomation(config)
        
    def start(self, config: Optional[BrowserConfig] = None) -> bool:
        return asyncio.run(self._async_browser.start(config))
    
    def stop(self):
        asyncio.run(self._async_browser.stop())
    
    def navigate(self, url: str) -> bool:
        return asyncio.run(self._async_browser.navigate(url))
    
    def click(self, selector: str) -> bool:
        return asyncio.run(self._async_browser.click(selector))
    
    def fill(self, selector: str, value: str) -> bool:
        return asyncio.run(self._async_browser.fill(selector, value))
    
    def get_content(self) -> str:
        return asyncio.run(self._async_browser.get_content())
    
    def screenshot(self, path: Optional[str] = None) -> Optional[str]:
        return asyncio.run(self._async_browser.screenshot(path))
    
    def is_connected(self) -> bool:
        return self._async_browser.is_connected()
