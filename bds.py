from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urljoin
import csv
import time
import random
import datetime

url = "https://batdongsan.com.vn/nha-dat-ban-tp-hcm"
base_url = "https://batdongsan.com.vn/"
max_pages = 1 # số trang cần cào
output_file = f"bds_{datetime.datetime.now().strftime('%d%m%Y')}.csv"

all_data = []
all_columns = set()


def random_delay(min_s, max_s, desc=""):
    delay = random.uniform(min_s, max_s)
    print(f" Nghỉ {delay:.2f}s {desc}...")
    time.sleep(delay)


def scroll_to_bottom(page, max_scrolls=8):
    """Cuộn trang để load hết dữ liệu"""
    print(" Đang cuộn trang để load dữ liệu...")
    for i in range(max_scrolls):
        page.mouse.wheel(0, 3000)
        time.sleep(1.5)
        links = page.query_selector_all("a.js__product-link-for-product-id")
        if len(links) >= 20:
            break
    print(f" Đã cuộn xong, phát hiện {len(links)} tin đăng.")
    return links


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=150)

    for page_num in range(1, max_pages + 1):
        page_url = url if page_num == 1 else f"{url}/p{page_num}"
        print(f"\n Đang mở trang {page_num}: {page_url}")

        # --- Mỗi trang mở trong 1 tab mới ---
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )

        # Thêm headers & xóa cookie/cache
        context = page.context
        context.clear_cookies()
        context.set_default_timeout(60000)

        for attempt in range(3):
            try:
                page.goto(page_url, wait_until="domcontentloaded")
                page.wait_for_selector("body", timeout=15000)
                print(f" Trang {page_num} đã load thành công (lần {attempt+1}).")
                break
            except PlaywrightTimeoutError:
                print(f"⚠ Trang {page_num} load chậm. Thử lại ({attempt+1}/3)...")
                random_delay(5, 10)
        else:
            print(f" Bỏ qua trang {page_num} vì không thể tải được.")
            page.close()
            continue

        links = scroll_to_bottom(page)

        hrefs = []
        for a in links:
            href = a.get_attribute("href")
            if href and href not in hrefs:
                hrefs.append(urljoin(base_url, href))
        print(f" Thu thập được {len(hrefs)} liên kết trong trang {page_num}.\n")

        # --- Mở từng bài đăng trong tab mới ---
        for idx, link in enumerate(hrefs, start=1):
            print(f" [{page_num}.{idx}] Đang truy cập: {link}")
            detail_page = browser.new_page()
            try:
                detail_page.goto(link, wait_until="domcontentloaded", timeout=60000)
                detail_page.wait_for_selector(".re__pr-specs-content-item-title", timeout=15000)

                titles = detail_page.query_selector_all(".re__pr-specs-content-item-title")
                values = detail_page.query_selector_all(".re__pr-specs-content-item-value")

                if titles and values:
                    item = {"Link": link}
                    for t, v in zip(titles, values):
                        t_text = t.inner_text().strip()
                        v_text = v.inner_text().strip()
                        item[t_text] = v_text
                        all_columns.add(t_text)

                    all_data.append(item)
                    print(f" Lấy được {len(item)-1} thuộc tính.")
                else:
                    print(" Không tìm thấy phần tử chi tiết cần lấy.")

            except PlaywrightTimeoutError:
                print(f" Timeout khi tải {link}.")
            except Exception as e:
                print(f"Lỗi khi truy cập {link}: {e}")
            finally:
                detail_page.close()

            random_delay(4, 8, "tránh bị Cloudflare chặn")

        page.close()
        random_delay(10, 18, f"trước khi sang trang {page_num + 1}")

    browser.close()

columns = ["Link"] + sorted(all_columns)
with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    for row in all_data:
        writer.writerow(row)

print(f"\n Hoàn tất! Đã lưu {len(all_data)} tin vào file: {output_file}")
