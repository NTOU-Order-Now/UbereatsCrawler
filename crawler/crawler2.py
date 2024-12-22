from playwright.sync_api import Playwright, sync_playwright, expect
import json
import time
from multiprocessing import Process, Pool, Manager
import math

def scrape_store(store_info):
    index, store_name, home_page = store_info
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })
        
        # 前往首頁
        page.goto(home_page)
        page.wait_for_selector('h3', timeout=10000)
        
        try:
            # 跳過特定商店
            if store_name in ['統一超商 海洋門市', '全聯福利中心  基隆海大', '美廉社 基隆祥豐店']:
                return None
                
            store = page.get_by_text(store_name).nth(0)
            if not store:
                return None
                
            store.scroll_into_view_if_needed()
            store.click()
            
            # 等待並獲取資料
            page.wait_for_selector('h1', timeout=10000)
            name = page.query_selector('h1').text_content()
            
            description_xpath = '/html/body/div[1]/div[1]/div[1]/div[2]/main/div/div[2]/div/div/div[1]/div[2]'
            description = page.locator(f'xpath={description_xpath}')
            description = description.text_content() if description.count() > 0 else ''
            
            address_xpath = '/html/body/div[1]/div[1]/div[1]/div[2]/main/div/div[2]/div/div/div[3]/div/section/ul/button[1]/div[2]/div[1]/p[1]'
            address = page.locator(f'xpath={address_xpath}')
            address = address.text_content() if address.count() > 0 else ''
            
            picture_xpath = '/html/body/div[1]/div[1]/div[1]/div[2]/main/div/div[1]/div/div[1]/img'
            picture = page.locator(f'xpath={picture_xpath}')
            
            if picture.count() > 0:
                srcset = picture.get_attribute('srcset')
                if srcset:
                    sources = srcset.split(',')
                    highest_res_url = sources[-1].strip().split(' ')[0]
                    picture = highest_res_url
            else:
                picture = ''
            
            store_data = {
                'name': name,
                'description': description,
                'address': address,
                'picture': picture
            }
            
            print(f'已完成 {index}: {name} 的爬取')
            return store_data
            
        except Exception as e:
            print(f'爬取 {store_name} 時發生錯誤: {str(e)}')
            return None
        
        finally:
            context.close()
            browser.close()

def save_to_json(data):
    with open('stores_data2.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    # 初始化首頁資料
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })

        page.goto("https://www.ubereats.com/tw")
        page.get_by_placeholder("輸入外送地址").click()
        page.keyboard.type("基隆海洋大學", delay=0)
        page.get_by_role("option", name="海洋大學 台灣基隆中正區北寧路").click()
        
        page.wait_for_selector('h3', timeout=5000)
        stores = page.query_selector_all('h3')
        stores_name = [store.text_content() for store in stores]
        page.wait_for_load_state('load')
        home_page = page.url
        
        seen = set()
        unique_stores_name = [name for name in stores_name if name not in seen and not seen.add(name)]
        
        context.close()
        browser.close()
    
    # 準備多進程參數
    store_info_list = [(i, name, home_page) for i, name in enumerate(unique_stores_name)]
    
    # 使用進程池執行爬蟲
    with Pool(processes=8) as pool:  # 可以根據您的電腦配置調整進程數
        results = pool.map(scrape_store, store_info_list)
    
    # 過濾掉 None 結果並保存
    valid_results = [r for r in results if r is not None]
    save_to_json(valid_results)
    print("所有資料已成功儲存至 stores_data.json")

if __name__ == '__main__':
    main()