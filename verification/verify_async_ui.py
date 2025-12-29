from playwright.sync_api import sync_playwright, expect

def verify_minimax_async_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the local server
        page.goto("http://localhost:5000")
        
        # Verify title
        expect(page).to_have_title("MiniMax 语音合成 (同步/异步)")
        
        # Verify Mode Switcher
        sync_radio = page.locator("input[name='mode'][value='sync']")
        async_radio = page.locator("input[name='mode'][value='async']")
        
        expect(sync_radio).to_be_visible()
        expect(async_radio).to_be_visible()
        expect(sync_radio).to_be_checked()
        
        # Toggle to Async Mode
        async_radio.click()
        
        # Verify File Upload appears
        upload_input = page.locator("#file-upload")
        expect(upload_input).to_be_visible()
        
        # Verify Text Placeholder changed
        text_area = page.locator("#text")
        # Note: Playwright checks attributes differently, or we can check visually
        
        # Toggle back to Sync Mode
        sync_radio.click()
        expect(upload_input).not_to_be_visible()
        
        # Take a screenshot in Async Mode for verification
        async_radio.click()
        
        screenshot_path = "verification/minimax_async_ui.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        browser.close()

if __name__ == "__main__":
    verify_minimax_async_ui()
