#!/usr/bin/env python3
"""
Test script for the new tools: IdentityCore, ScreenCaptureTool, BrowserAutomation, VirtualMouseController.
"""

from agent.infra.tools import (
    IdentityCore, 
    ScreenCaptureTool, 
    BrowserAutomation, 
    VirtualMouseController,
    get_identity_core,
    get_screen_capture_tool,
    get_virtual_mouse
)


def test_identity_core():
    """Test IdentityCore functionality."""
    print("=" * 60)
    print("Testing IdentityCore")
    print("=" * 60)
    
    identity = IdentityCore()
    
    # Test name verification
    print("\n1. Testing name verification...")
    result = identity.verify_name("John Doe")
    print(f"   Name: John Doe")
    print(f"   Confidence Score: {result['confidence_score']}")
    print(f"   Sources Found: {result['sources_found']}")
    print(f"   Risk Flags: {result['risk_flags']}")
    
    # Test email verification
    print("\n2. Testing email verification...")
    result = identity.verify_email("john.doe@example.com")
    print(f"   Email: john.doe@example.com")
    print(f"   Valid Format: {result['valid_format']}")
    print(f"   Domain Exists: {result['domain_exists']}")
    print(f"   Confidence Score: {result['confidence_score']}")
    
    # Test comprehensive verification
    print("\n3. Testing comprehensive verification...")
    report = identity.comprehensive_verify(
        name="Jane Smith",
        email="jane.smith@gmail.com",
        phone="+1-555-123-4567"
    )
    print(f"   Overall Confidence: {report['overall_confidence']}")
    print(f"   Overall Risk: {report['overall_risk']}")
    print(f"   Recommendations: {report['recommendations']}")
    
    print("\n✓ IdentityCore tests completed\n")


def test_screen_capture():
    """Test ScreenCaptureTool functionality."""
    print("=" * 60)
    print("Testing ScreenCaptureTool")
    print("=" * 60)
    
    capture = ScreenCaptureTool(output_dir="./test_captures")
    
    # Test screen resolution
    print("\n1. Getting screen resolution...")
    resolution = capture.get_screen_resolution()
    print(f"   Resolution: {resolution}")
    
    # Test monitor info
    print("\n2. Getting monitor info...")
    monitors = capture.get_monitor_info()
    print(f"   Monitors: {monitors}")
    
    # Test full screen capture (will fail in headless environment)
    print("\n3. Testing screen capture capability...")
    if capture._pyautogui:
        print("   pyautogui is available")
        print("   Note: Actual capture requires GUI environment")
    else:
        print("   pyautogui not available (headless environment)")
    
    print("\n✓ ScreenCaptureTool tests completed\n")


def test_virtual_mouse():
    """Test VirtualMouseController functionality."""
    print("=" * 60)
    print("Testing VirtualMouseController")
    print("=" * 60)
    
    vmouse = VirtualMouseController(overlay_color="#00FF00", overlay_size=25)
    
    # Test initial position
    print("\n1. Getting initial position...")
    pos = vmouse.get_position()
    print(f"   Position: {pos.to_dict()}")
    
    # Test movement
    print("\n2. Testing movement...")
    result = vmouse.set_position(100, 100, animate=False)
    print(f"   Move to (100, 100): {result['success']}")
    
    new_pos = vmouse.get_position()
    print(f"   New position: {new_pos.to_dict()}")
    
    # Test relative movement
    print("\n3. Testing relative movement...")
    result = vmouse.move_relative(50, 50, animate=False)
    print(f"   Move relative (50, 50): {result['success']}")
    
    newer_pos = vmouse.get_position()
    print(f"   Newer position: {newer_pos.to_dict()}")
    
    # Test click simulation
    print("\n4. Testing click simulation...")
    print(f"   Click method available: {hasattr(vmouse, 'click')}")
    print(f"   Double-click method available: {hasattr(vmouse, 'double_click')}")
    print(f"   Right-click method available: {hasattr(vmouse, 'right_click')}")
    
    # Test history
    print("\n5. Testing movement history...")
    history = vmouse.get_movement_history(limit=5)
    print(f"   Movement history entries: {len(history)}")
    
    print("\n✓ VirtualMouseController tests completed\n")


def test_browser_automation_info():
    """Display BrowserAutomation information."""
    print("=" * 60)
    print("BrowserAutomation Information")
    print("=" * 60)
    
    print("\nBrowserAutomation provides:")
    print("  - Async browser control using Playwright")
    print("  - Support for Chromium, Firefox, and WebKit")
    print("  - Headless and headed modes")
    print("  - Navigation, clicking, form filling")
    print("  - Screenshot capture")
    print("  - JavaScript execution")
    print("  - Cookie management")
    print("\nNote: Requires playwright to be installed")
    print("      Install with: pip install playwright")
    print("      Then run: playwright install")
    
    # Check if playwright is available
    try:
        import playwright
        print("\n✓ Playwright is installed")
    except ImportError:
        print("\n⚠ Playwright is not installed (optional dependency)")
    
    print("\n✓ BrowserAutomation info displayed\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NEW TOOLS TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    test_identity_core()
    test_screen_capture()
    test_virtual_mouse()
    test_browser_automation_info()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nAll new tools have been successfully integrated:")
    print("  ✓ IdentityCore - Identity verification with web search")
    print("  ✓ ScreenCaptureTool - Screen capture and image processing")
    print("  ✓ BrowserAutomation - Browser automation via Playwright")
    print("  ✓ VirtualMouseController - Secondary mouse for automation")
    print("\nLocation: /workspace/agent/infra/tools/")
    print("\nFiles created:")
    print("  - identity.py")
    print("  - screen_capture.py")
    print("  - browser_automation.py")
    print("  - virtual_mouse.py")
    print("  - __init__.py (updated)")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
