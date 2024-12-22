from playwright.sync_api import Playwright, sync_playwright, expect
import json
import time
    
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
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
    
    # count = 30
    count = len(unique_stores_name)
    print(f'Find {count} stores')
    
    store_data = []
    
    for i in range(count):
        print(f'{i}: {unique_stores_name[i]}')
        store = page.get_by_text(unique_stores_name[i]).nth(0)
        
        if not store:
            continue
        if unique_stores_name[i] == '統一超商 海洋門市':
            continue
        if unique_stores_name[i] == '全聯福利中心  基隆海大':
            continue
        if unique_stores_name[i] == '美廉社 基隆祥豐店':
            continue
        
        store.scroll_into_view_if_needed()
        store.click()
        
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
        
        print(f'店名: {name}')
        print(f'描述: {description}')
        print(f'地址: {address}')
        print(f'圖片: {picture}')
        print('---' * 10)
        
        store_data.append({
            'name': name,
            'description': description,
            'address': address,
            'picture': picture
        })
    
        try:
            button = page.wait_for_selector('button[aria-label="關閉"]', timeout=2000)
            while button.is_visible():
                button.click()
                try:
                    button = page.wait_for_selector('button[aria-label="關閉"]', timeout=2000)
                except:
                    print("沒有找到按鈕")
                    break
        except:
            print("沒有找到按鈕")
        
        page.goto(home_page)
        page.wait_for_selector('h3', timeout=10000)
        
        with open('stores_data.json', 'w', encoding='utf-8') as f:
            json.dump(store_data, f, ensure_ascii=False, indent=4)
    
    
    print("資料已成功儲存至 stores_data.json")
    
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
