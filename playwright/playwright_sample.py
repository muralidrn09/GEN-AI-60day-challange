# google_latest_cricket_headless.py
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError

QUERY = "latest cricket news"
HEADLESS = False  # set True to run headless
COMMON_DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# User-provided XPath for Google search input:
SEARCH_INPUT_XPATH = "//*[@id='APjFqb']"

async def run_google_flow(query=QUERY):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent=COMMON_DESKTOP_UA,
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            java_script_enabled=True,
        )
        page = await context.new_page()

        try:
            # 1) Go to Google
            await page.goto("https://www.google.com", timeout=60000)

            # 1.a) Best-effort: accept cookie/consent dialogs if present
            consent_selectors = [
                "button#bnp_btn_accept",
                "button[title='Accept']",
                "button:has-text('I agree')",
                "button:has-text('Accept all')",
                "form[action*='consent'] button[type='submit']"
            ]
            for sel in consent_selectors:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        await el.click()
                        # small wait for overlay to disappear
                        await page.wait_for_timeout(500)
                        break
                except Exception:
                    pass

            # 2) Wait for Google search input using the XPath you provided
            try:
                await page.wait_for_selector(f"xpath={SEARCH_INPUT_XPATH}", timeout=15000)
            except PWTimeoutError:
                print("⚠️ Search input not found by XPath within timeout.")
                # fallback to common selector
                try:
                    await page.wait_for_selector("input[name='q']", timeout=8000)
                    print("Fallback: found input[name='q']")
                except Exception:
                    raise RuntimeError("Search input not found on the page.")

            # 3) Fill the search box and press Enter
            try:
                await page.locator(f"xpath={SEARCH_INPUT_XPATH}").fill(query)
            except Exception:
                # fallback: fill by name attribute
                await page.fill("input[name='q']", query)

            await page.keyboard.press("Enter")

            # 4) Wait for search results to appear
            try:
                await page.wait_for_selector("div#search h3", timeout=15000)
            except PWTimeoutError:
                print("⚠️ Search results did not appear in time. Possible robot/captcha or slow network.")

            # 5) Detect captcha/robot interstitial (Google "unusual traffic" page)
            current_url = page.url
            if "/sorry/" in current_url or "consent" in current_url or "recaptcha" in current_url:
                print("🚨 Google is showing a robot/consent/recaptcha page. Manual intervention required.")
                print("URL:", current_url)
            else:
                # 6) Click the first result's title (h3). This clicks the parent <a>.
                try:
                    first_result = page.locator("div#search h3").first
                    await first_result.click(timeout=10000)
                    # Wait for navigation to finish
                    await page.wait_for_load_state("networkidle", timeout=30000)
                except Exception as e:
                    print("⚠️ Clicking first result failed:", repr(e))
                    # Try alternate selector
                    try:
                        await page.locator("div.g a").first.click(timeout=10000)
                        await page.wait_for_load_state("networkidle", timeout=30000)
                    except Exception as e2:
                        print("Fallback click also failed:", repr(e2))

                # 7) Output opened page info
                url = page.url
                title = await page.title()
                print("✅ Opened page")
                print("URL:", url)
                print("Title:", title)

                # 8) Try to extract article headline (h1)
                try:
                    h1 = await page.query_selector("h1")
                    if h1:
                        text = (await h1.inner_text()).strip()
                        if text:
                            print("Headline (detected):", text)
                        else:
                            print("Headline: (empty h1)")
                    else:
                        print("Headline: (no h1 found)")
                except Exception:
                    print("Headline: (error detecting h1)")

        except Exception as exc:
            print("❌ Error during automated flow:", repr(exc))
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_google_flow())
