from playwright.sync_api import sync_playwright, expect
import re

def verify_bootstrap_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the local server
        page.goto("http://localhost:5000")
        
        # Verify title
        expect(page).to_have_title("MiniMax 语音合成助手")
        
        # Verify Bootstrap classes
        # Check for card
        expect(page.locator(".card")).to_be_visible()
        # Check for form-control inputs (using regex to match 'form-control' inside class string)
        expect(page.locator("#api_key")).to_have_class(re.compile(r"form-control"))
        # Check for button styles
        expect(page.locator("#generate-btn")).to_have_class(re.compile(r"btn-primary"))
        
        # Verify Layout (Mode Switcher)
        expect(page.locator(".btn-group")).to_be_visible()
        
        # Take a screenshot
        screenshot_path = "verification/bootstrap_ui.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        browser.close()

if __name__ == "__main__":
    verify_bootstrap_ui()
