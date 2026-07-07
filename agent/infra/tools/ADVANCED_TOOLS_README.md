# Advanced Tools Integration

This document describes the new advanced tools added to the agent infrastructure.

## Overview

Four new tool categories have been integrated:

1. **Identity Core** - Identity verification with web search
2. **Screen Capture Tool** - Screenshot and screen recording capabilities  
3. **Browser Automation** - Browser control using Playwright
4. **Virtual Mouse** - Secondary mouse controller for agent automation

## 1. Identity Core (`identity.py`)

Identity verification system that cross-references information from multiple web sources.

### Features

- **Name Verification**: Searches web sources to verify a person's identity
- **Email Verification**: Validates email format, domain existence, and detects disposable emails
- **Username Verification**: Checks username presence across multiple platforms
- **Cross-Reference**: Comprehensive verification combining multiple attributes

### Usage

```python
from agent.infra.tools import get_identity_core

identity = get_identity_core()

# Verify a name
result = identity.verify_name("John Doe", context="software engineer")
print(f"Confidence: {result.confidence_score}")
print(f"Social profiles: {result.social_profiles}")

# Verify an email
email_result = identity.verify_email("john@example.com")
print(f"Valid: {email_result['valid_format']}")
print(f"Disposable: {email_result['disposable']}")

# Cross-reference multiple attributes
report = identity.cross_reference(
    name="John Doe",
    email="john@example.com",
    username="johndoe"
)
print(f"Overall confidence: {report['overall_confidence']}")
```

### API Reference

- `verify_name(name: str, context: Optional[str]) -> IdentityRecord`
- `verify_email(email: str) -> Dict[str, Any]`
- `verify_username(username: str, platforms: Optional[List[str]]) -> Dict[str, Any]`
- `cross_reference(name, email, username) -> Dict[str, Any]`
- `get_verification_history(limit: int) -> List[Dict]`

## 2. Screen Capture Tool (`screen_capture.py`)

Screenshot and screen capture capabilities using PyAutoGUI.

### Features

- **Full Screen Capture**: Capture entire screen
- **Region Capture**: Capture specific screen regions
- **Window Capture**: Capture specific windows (platform-dependent)
- **Mouse Position**: Get current mouse coordinates
- **Image Search**: Find images on screen
- **History Tracking**: Log all captures

### Usage

```python
from agent.infra.tools import get_screen_capture_tool

capture = get_screen_capture_tool()

# Capture full screen
result = capture.capture_full_screen(save=True)
print(f"Saved to: {result['filepath']}")

# Capture a region
region = capture.capture_region(x=100, y=100, width=800, height=600)

# Get screen info
info = capture.get_screen_info()
print(f"Screen size: {info['primary_screen']['width']}x{info['primary_screen']['height']}")

# Find image on screen
location = capture.find_image_on_screen("/path/to/button.png", confidence=0.9)
if location['found']:
    print(f"Found at: {location['location']['center']}")
```

### API Reference

- `capture_full_screen(save=True, filename=None) -> Dict[str, Any]`
- `capture_region(x, y, width, height, save=True) -> Dict[str, Any]`
- `capture_window(window_title=None, save=True) -> Dict[str, Any]`
- `get_screen_info() -> Dict[str, Any]`
- `get_mouse_position() -> Dict[str, int]`
- `find_image_on_screen(image_path, confidence=0.9) -> Optional[Dict]`

### Dependencies

```bash
pip install pyautogui
```

## 3. Browser Automation (`browser_automation.py`)

Browser control using Playwright for Chrome, Firefox, and WebKit.

### Features

- **Multi-Browser Support**: Chromium, Firefox, WebKit
- **Navigation**: Go to URLs, wait for page loads
- **Interaction**: Click, fill, press keys, hover
- **Content Extraction**: Get HTML, text, screenshots
- **JavaScript Execution**: Run custom JS in page context
- **Cookie Management**: Set, get, clear cookies
- **Async & Sync APIs**: Both async and synchronous interfaces

### Usage

```python
from agent.infra.tools import SyncBrowserAutomation, BrowserConfig

# Configure browser
config = BrowserConfig(
    browser_type="chromium",
    headless=True,
    viewport_width=1920,
    viewport_height=1080
)

# Create browser instance
browser = SyncBrowserAutomation(config)

# Start browser
browser.start()

# Navigate to page
browser.navigate("https://example.com")

# Interact with page
browser.fill("#search-input", "hello world")
browser.click("#search-button")

# Wait for content
browser.wait_for_selector(".results")

# Get content
title = browser.get_title()
content = browser.get_text()

# Take screenshot
screenshot_path = browser.screenshot("/tmp/example.png")

# Stop browser
browser.stop()
```

### Async Usage

```python
import asyncio
from agent.infra.tools import BrowserAutomation

async def main():
    browser = BrowserAutomation()
    await browser.start()
    await browser.navigate("https://example.com")
    content = await browser.get_content()
    await browser.stop()

asyncio.run(main())
```

### API Reference

- `start(config=None) -> bool`
- `stop()`
- `navigate(url, wait_until="domcontentloaded") -> bool`
- `click(selector, timeout=None) -> bool`
- `fill(selector, value) -> bool`
- `press(key) -> bool`
- `get_content() -> str`
- `get_text(selector=None) -> str`
- `screenshot(path=None, full_page=False) -> Optional[str]`
- `wait_for_selector(selector, state="visible") -> bool`
- `evaluate(javascript) -> Any`

### Dependencies

```bash
pip install playwright
playwright install  # Install browser binaries
```

## 4. Virtual Mouse (`virtual_mouse.py`)

Secondary mouse controller that operates independently from user's physical mouse.

### Features

- **Independent Control**: Separate from user's mouse
- **Safety Features**: User activity detection, safe zones
- **Movement Logging**: Track all movements
- **Pattern Movement**: Pre-defined movement patterns
- **Speed Control**: Adjustable movement speed
- **Button Control**: Left, right, middle clicks

### Usage

```python
from agent.infra.tools import get_virtual_mouse, MousePatterns

# Get virtual mouse instance
mouse = get_virtual_mouse(speed=1.0, safe_mode=True)

# Activate
mouse.activate()

# Move to position
mouse.move_to(500, 500)

# Relative movement
mouse.move_relative(100, 50)

# Click
mouse.click(button='left', clicks=1)
mouse.double_click()
mouse.right_click()

# Drag
mouse.drag_to(600, 600, duration=1.0)

# Scroll
mouse.scroll(amount=-100)  # Scroll down

# Use pre-defined patterns
pattern = MousePatterns.circle(center_x=960, center_y=540, radius=100)
mouse.move_in_pattern(pattern, speed=0.5)

# Get position
pos = mouse.get_position()
print(f"Current: ({pos.x}, {pos.y})")

# Deactivate when done
mouse.deactivate()
```

### Safety Features

The virtual mouse includes several safety features:

1. **User Activity Detection**: Pauses if user moves mouse significantly
2. **Safe Margins**: Keeps cursor away from screen edges
3. **Fail-Safe**: PyAutoGUI's fail-safe (move to corner to abort)
4. **Speed Limiting**: Prevents unnaturally fast movements

### API Reference

- `activate() -> bool`
- `deactivate()`
- `move_to(x, y, duration=None) -> bool`
- `move_relative(dx, dy, duration=None) -> bool`
- `click(button='left', clicks=1, interval=0.1) -> bool`
- `double_click(button='left') -> bool`
- `right_click() -> bool`
- `drag_to(x, y, duration=1.0, button='left') -> bool`
- `scroll(amount, x=None, y=None) -> bool`
- `get_position() -> MousePosition`
- `move_in_pattern(pattern, speed=1.0) -> bool`

### Mouse Patterns

Pre-defined movement patterns available:

- `MousePatterns.circle(center_x, center_y, radius, steps=36)`
- `MousePatterns.figure_eight(center_x, center_y, width, height)`
- `MousePatterns.grid(start_x, start_y, cols, rows, cell_width, cell_height)`

### Dependencies

```bash
pip install pyautogui
```

## Integration with LLM Tools

All new tools can be registered with the LLM tools interface:

```python
from agent.infra.tools import LLMTools, get_identity_core, get_screen_capture_tool

llm_tools = LLMTools()

# Register identity verification
identity = get_identity_core()
llm_tools.register_tool(
    name="verify_identity",
    description="Verify a person's identity using web search",
    parameters={...},
    function=identity.verify_name
)

# Register screen capture
capture = get_screen_capture_tool()
llm_tools.register_tool(
    name="take_screenshot",
    description="Take a screenshot of the current screen",
    parameters={...},
    function=capture.capture_full_screen
)
```

## Security Considerations

1. **Identity Core**: 
   - Respects rate limiting on web searches
   - Caches results to minimize requests
   - Does not store sensitive data persistently

2. **Screen Capture**:
   - Saves to temporary directory by default
   - History can be cleared programmatically
   - User consent recommended before capturing

3. **Browser Automation**:
   - Runs in isolated browser context
   - Cookies cleared on stop by default
   - Proxy support for additional isolation

4. **Virtual Mouse**:
   - Safe mode yields control to user
   - Movement history logged for audit
   - Failsafe prevents runaway cursor

## Troubleshooting

### Import Errors

Ensure dependencies are installed:
```bash
pip install pyautogui playwright beautifulsoup4 requests
playwright install
```

### Permission Issues

Some features may require additional permissions:
- Screen capture may need accessibility permissions (macOS)
- Browser automation may need display access (Linux)

### Rate Limiting

Web search tools include built-in rate limiting. If you encounter issues:
- Increase delays between requests
- Use caching where appropriate
- Consider API-based alternatives for production use
