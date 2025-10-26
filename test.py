from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import time

url = "https://batdongsan.com.vn/nha-dat-ban-tp-hcm"
base_url = "https://batdongsan.com.vn/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    )

    print(f"🌐 Đang mở trang danh sách: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=360000)
    time.sleep(3)

    # Lấy tất cả href của tin đăng
    links = page.query_selector_all("a.js__product-link-for-product-id")
    hrefs = []
    for a in links:
        href = a.get_attribute("href")
        if href and href not in hrefs:
            hrefs.append(urljoin(base_url, href))

    print(f"✅ Đã thu thập {len(hrefs)} liên kết tin đăng trong trang 1.\n")

    # Duyệt qua từng link để lấy thông tin chi tiết
    for idx, link in enumerate(hrefs, start=1):
        print(f"🕵️‍♂️ [{idx}] Đang truy cập: {link}")
        detail_page = browser.new_page()
        try:
            detail_page.goto(link, wait_until="domcontentloaded", timeout=360000)
            time.sleep(2)

            titles = detail_page.query_selector_all(".re__pr-specs-content-item-title")
            values = detail_page.query_selector_all(".re__pr-specs-content-item-value")

            if titles and values:
                print("📋 Thông tin chi tiết:")
                for t, v in zip(titles, values):
                    t_text = t.inner_text().strip()
                    v_text = v.inner_text().strip()
                    print(f" - {t_text}: {v_text}")
            else:
                print("⚠️ Không tìm thấy phần tử chi tiết cần lấy.")

        except Exception as e:
            print(f"❌ Lỗi khi truy cập {link}: {e}")

        detail_page.close()
        print("-" * 50)
        time.sleep(1)  # nghỉ nhẹ giữa các lần truy cập

    browser.close()
