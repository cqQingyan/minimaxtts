from playwright.sync_api import sync_playwright, expect

def verify_minimax_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the local server
        page.goto("http://localhost:5000")
        
        # Verify title
        expect(page).to_have_title("MiniMax 异步长文本语音合成")
        
        # Verify inputs exist
        expect(page.locator("#api_key")).to_be_visible()
        expect(page.locator("#group_id")).to_be_visible()
        expect(page.locator("#voice_id")).to_be_visible()
        expect(page.locator("#text")).to_be_visible()
        expect(page.locator("#generate-btn")).to_be_visible()
        
        # Fill in some dummy data
        page.locator("#api_key").fill("dummy-api-key")
        page.locator("#group_id").fill("dummy-group-id")
        page.locator("#voice_id").fill("audiobook_male_1")
        page.locator("#text").fill("这是一个测试文本。")
        
        # Take a screenshot
        screenshot_path = "verification/minimax_ui.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        browser.close()

if __name__ == "__main__":
    verify_minimax_page()
