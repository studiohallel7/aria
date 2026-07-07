"""
Browser Automation - Browser automation using Playwright.
Supports Chrome, Firefox, and WebKit with headless and headed modes.
Provides web interaction, scraping, and testing capabilities.
"""

import asyncio
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from pathlib import Path


class BrowserAutomation:
    """
    Browser automation tool using Playwright.
    Supports multiple browsers, headless mode, and advanced interactions.
    """
    
    def __init__(self, browser_type: str = "chromium", 
                 headless: bool = True,
                 slow_mo: int = 0):
        """
        Initialize browser automation.
        
        Args:
            browser_type: Type of browser ("chromium", "firefox", "webkit")
            headless: Run browser in headless mode
            slow_mo: Slow down operations by specified milliseconds
        """
        self.browser_type = browser_type
        self.headless = headless
        self.slow_mo = slow_mo
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._is_connected = False
        self.action_history = []
    
    async def connect(self) -> bool:
        """
        Connect to browser and create a new context and page.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            from playwright.async_api import async_playwright
            
            self._playwright = await async_playwright().start()
            
            # Launch browser based on type
            if self.browser_type == "chromium":
                self._browser = await self._playwright.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )
            elif self.browser_type == "firefox":
                self._browser = await self._playwright.firefox.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )
            elif self.browser_type == "webkit":
                self._browser = await self._playwright.webkit.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo
                )
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            # Create browser context
            self._context = await self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            # Create page
            self._page = await self._context.new_page()
            self._is_connected = True
            
            self._log_action("connect", {
                "browser_type": self.browser_type,
                "headless": self.headless
            })
            
            return True
            
        except Exception as e:
            print(f"Error connecting to browser: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            
            self._is_connected = False
            self._log_action("disconnect", {})
            
        except Exception as e:
            print(f"Error disconnecting: {e}")
    
    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation successful
                       ("load", "domcontentloaded", "networkidle", "commit")
        
        Returns:
            Navigation result with status and metadata
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            response = await self._page.goto(url, wait_until=wait_until)
            
            result = {
                "success": True,
                "url": url,
                "status": response.status if response else None,
                "title": await self._page.title(),
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("navigate", {"url": url})
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "url": url}
    
    async def click(self, selector: str, timeout: int = 30000) -> Dict[str, Any]:
        """
        Click an element on the page.
        
        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait for element
        
        Returns:
            Click result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._page.click(selector, timeout=timeout)
            
            result = {
                "success": True,
                "selector": selector,
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("click", {"selector": selector})
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}
    
    async def fill(self, selector: str, value: str, timeout: int = 30000) -> Dict[str, Any]:
        """
        Fill an input field with text.
        
        Args:
            selector: CSS selector for the input field
            value: Text to fill
            timeout: Maximum time to wait for element
        
        Returns:
            Fill result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._page.fill(selector, value, timeout=timeout)
            
            result = {
                "success": True,
                "selector": selector,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("fill", {"selector": selector, "value": value})
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}
    
    async def type_text(self, selector: str, text: str, 
                       delay: int = 50) -> Dict[str, Any]:
        """
        Type text character by character (simulates real typing).
        
        Args:
            selector: CSS selector for the input field
            text: Text to type
            delay: Delay between keystrokes in milliseconds
        
        Returns:
            Type result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._page.type(selector, text, delay=delay)
            
            result = {
                "success": True,
                "selector": selector,
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("type", {"selector": selector, "text": text})
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}
    
    async def get_content(self) -> Dict[str, Any]:
        """
        Get the full HTML content of the page.
        
        Returns:
            Page content
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            content = await self._page.content()
            title = await self._page.title()
            
            result = {
                "success": True,
                "url": self._page.url,
                "title": title,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("get_content", {})
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_text(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Get text content from the page or a specific element.
        
        Args:
            selector: CSS selector (optional, gets entire page if not provided)
        
        Returns:
            Text content
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            if selector:
                text = await self._page.text_content(selector)
            else:
                text = await self._page.inner_text("body")
            
            result = {
                "success": True,
                "text": text,
                "selector": selector,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def screenshot(self, path: Optional[str] = None,
                        full_page: bool = False) -> Dict[str, Any]:
        """
        Take a screenshot of the page.
        
        Args:
            path: File path to save screenshot (optional)
            full_page: Capture full scrollable page
        
        Returns:
            Screenshot result with base64 data or file path
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            screenshot_bytes = await self._page.screenshot(
                path=path,
                full_page=full_page
            )
            
            result = {
                "success": True,
                "path": path,
                "has_data": screenshot_bytes is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            self._log_action("screenshot", {"path": path, "full_page": full_page})
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def evaluate(self, javascript: str) -> Dict[str, Any]:
        """
        Execute JavaScript code in the page context.
        
        Args:
            javascript: JavaScript code to execute
        
        Returns:
            Execution result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            result = await self._page.evaluate(javascript)
            
            return {
                "success": True,
                "result": result,
                "javascript": javascript,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "javascript": javascript}
    
    async def wait_for_selector(self, selector: str, 
                               state: str = "visible",
                               timeout: int = 30000) -> Dict[str, Any]:
        """
        Wait for an element to appear/disappear.
        
        Args:
            selector: CSS selector to wait for
            state: State to wait for ("visible", "hidden", "attached", "detached")
            timeout: Maximum wait time in milliseconds
        
        Returns:
            Wait result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._page.wait_for_selector(selector, state=state, timeout=timeout)
            
            return {
                "success": True,
                "selector": selector,
                "state": state,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}
    
    async def wait_for_timeout(self, milliseconds: int) -> Dict[str, Any]:
        """
        Wait for a specified amount of time.
        
        Args:
            milliseconds: Time to wait in milliseconds
        
        Returns:
            Wait result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._page.wait_for_timeout(milliseconds)
            
            return {
                "success": True,
                "waited_ms": milliseconds,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def select_option(self, selector: str, 
                           value: str) -> Dict[str, Any]:
        """
        Select an option from a dropdown.
        
        Args:
            selector: CSS selector for the select element
            value: Value to select
        
        Returns:
            Selection result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._page.select_option(selector, value)
            
            return {
                "success": True,
                "selector": selector,
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}
    
    async def hover(self, selector: str) -> Dict[str, Any]:
        """
        Hover over an element.
        
        Args:
            selector: CSS selector for the element
        
        Returns:
            Hover result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._page.hover(selector)
            
            return {
                "success": True,
                "selector": selector,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "selector": selector}
    
    async def get_cookies(self) -> Dict[str, Any]:
        """Get all cookies from the current context."""
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            cookies = await self._context.cookies()
            
            return {
                "success": True,
                "cookies": cookies,
                "count": len(cookies),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add cookies to the context.
        
        Args:
            cookies: List of cookie dictionaries
        
        Returns:
            Result
        """
        if not self._is_connected:
            return {"success": False, "error": "Not connected to browser"}
        
        try:
            await self._context.add_cookies(cookies)
            
            return {
                "success": True,
                "cookies_added": len(cookies),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log an action to the history."""
        self.action_history.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_action_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent action history."""
        return self.action_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear action history."""
        self.action_history = []


# Convenience class for synchronous usage
class BrowserAutomationSync:
    """Synchronous wrapper for BrowserAutomation."""
    
    def __init__(self, browser_type: str = "chromium", 
                 headless: bool = True,
                 slow_mo: int = 0):
        self._async_browser = BrowserAutomation(browser_type, headless, slow_mo)
        self._loop = None
    
    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            import asyncio
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop
    
    def connect(self) -> bool:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_browser.connect())
    
    def disconnect(self) -> None:
        loop = self._get_loop()
        loop.run_until_complete(self._async_browser.disconnect())
    
    def navigate(self, url: str, wait_until: str = "domcontentloaded") -> Dict[str, Any]:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_browser.navigate(url, wait_until))
    
    def click(self, selector: str, timeout: int = 30000) -> Dict[str, Any]:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_browser.click(selector, timeout))
    
    def fill(self, selector: str, value: str, timeout: int = 30000) -> Dict[str, Any]:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_browser.fill(selector, value, timeout))
    
    def get_content(self) -> Dict[str, Any]:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_browser.get_content())
    
    def screenshot(self, path: Optional[str] = None, 
                  full_page: bool = False) -> Dict[str, Any]:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_browser.screenshot(path, full_page))


# Global instance
_browser_automation: Optional[BrowserAutomation] = None


def get_browser_automation(browser_type: str = "chromium",
                          headless: bool = True) -> BrowserAutomation:
    """Get or create the global BrowserAutomation instance."""
    global _browser_automation
    if _browser_automation is None:
        _browser_automation = BrowserAutomation(browser_type, headless)
    return _browser_automation
