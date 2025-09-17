#!/usr/bin/env python3
"""Test the freemium assessment flow in browser."""

from playwright.sync_api import sync_playwright
import time


def test_freemium_flow():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=False,
        )  # Set headless=False to see what's happening
        context = browser.new_context()
        page = context.new_page()

        # Navigate to freemium page
        print("1. Navigating to freemium page...")
        page.goto("http://localhost:3000/freemium")
        page.wait_for_load_state("networkidle")

        # Fill in email
        print("2. Filling email form...")
        email_input = page.locator('input[type="email"]')
        email_input.fill("test_browser@example.com")

        # Check marketing consent
        consent_checkbox = page.locator("#marketing-consent")
        consent_checkbox.check()

        # Click submit button
        print("3. Submitting form...")
        submit_button = page.locator('button:has-text("Start Free Assessment")')
        submit_button.click()

        # Wait for navigation or response
        print("4. Waiting for response...")
        time.sleep(3)  # Give it time to process

        # Check current URL
        current_url = page.url
        print(f"Current URL after submission: {current_url}")

        # Check for any error messages or loading states
        page_content = page.content()

        # Look for specific elements
        if "loading" in page_content.lower():
            print("⚠️  Page shows loading state")

        if "dashboard" in page_content.lower():
            print("⚠️  Page mentions dashboard")

        if "assessment" in current_url:
            print("✅ Redirected to assessment page")
            # Check if questions are displayed
            page.wait_for_load_state("networkidle")

            # Look for question elements
            question_elements = page.locator("h1, h2, h3").all_text_contents()
            print(f"Found headings: {question_elements}")

            # Check for error messages
            error_elements = page.locator(
                '[role="alert"], .error, .alert'
            ).all_text_contents()
            if error_elements:
                print(f"⚠️  Error messages found: {error_elements}")

        # Take a screenshot
        page.screenshot(path="freemium_flow_result.png")
        print("5. Screenshot saved as freemium_flow_result.png")

        # Keep browser open for debugging
        input("Press Enter to close browser...")

        browser.close()


if __name__ == "__main__":
    test_freemium_flow()
