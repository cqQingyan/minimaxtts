from playwright.sync_api import sync_playwright, expect

def verify_minimax_sync_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the local server
        page.goto("http://localhost:5000")
        
        # Verify title
        expect(page).to_have_title("MiniMax 同步语音合成")
        
        # Verify new "Check Connection" button exists
        check_btn = page.locator("#check-conn-btn")
        expect(check_btn).to_be_visible()
        expect(check_btn).to_have_text("检查连通性")
        
        # Verify other inputs
        expect(page.locator("#api_key")).to_be_visible()
        expect(page.locator("#group_id")).to_be_visible()
        
        # Click check connection (will fail with empty key, but we want to see the error message)
        check_btn.click()
        
        # Expect an alert or error status
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Fill in dummy key to trigger the actual API call logic (which will fail auth)
        page.locator("#api_key").fill("dummy-key")
        check_btn.click()
        
        # Wait for status div to appear
        status_div = page.locator("#connection-status")
        expect(status_div).to_be_visible(timeout=5000)
        
        # Take a screenshot
        screenshot_path = "verification/minimax_sync_ui.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        browser.close()

if __name__ == "__main__":
    verify_minimax_sync_ui()
