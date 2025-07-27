
import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import bs4
from database import SessionLocal, Product, create_tables

def safe_scroll_page(page):
    """Safely scroll the page with error handling"""
    try:
        if page.is_closed():
            return False
            
        last_height = page.evaluate("document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 10
        
        while scroll_attempts < max_scroll_attempts:
            try:
                page.evaluate("window.scrollBy(0, 100)")
                time.sleep(0.1)
                new_height = page.evaluate("() => window.scrollY ")
                
                if new_height == last_height:
                    page.evaluate("window.scrollBy(0, 100)")
                    new_height = page.evaluate("() => window.scrollY ")
                    time.sleep(1)
                    if new_height == last_height:
                        page.evaluate("window.scrollBy(0, 100)")
                        new_height = page.evaluate("() => window.scrollY ")
                        time.sleep(2)
                        if new_height == last_height:
                            scroll_attempts += 1
                            if scroll_attempts >= 3:
                                break
                        else:
                            scroll_attempts = 0
                    else:
                        scroll_attempts = 0
                else:
                    scroll_attempts = 0
                    
                last_height = new_height
            except Exception as scroll_error:
                print(f"Error during scrolling: {scroll_error}")
                break
        return True
    except Exception as e:
        print(f"Error in safe_scroll_page: {e}")
        return False





def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    with open('links.txt' , 'r') as f :
        links  = f.readlines()
    
    # Set up MySQL connection and table
    db = SessionLocal()
    create_tables()
    for link in links:
        if link.strip() and 'https://www.amazon.ae' in link:
            try:
                print(f"Processing Amazon link: {link.strip()}")
                page.goto(link , timeout=30000 , wait_until='load')
                page.wait_for_load_state('domcontentloaded')
            except Exception as e:
                print(f"Error loading Amazon page: {e}")
                continue
            while True:
                try:
                    # Use safe scrolling function
                    if not safe_scroll_page(page):
                        time.sleep(5)
                        if not safe_scroll_page(page):
                            print("Scrolling failed, moving to next link...")
                            break
                        
                    soup = bs4.BeautifulSoup(page.content(), "html.parser")
                    # time.sleep(2)
                    datas = soup.select('.puis-card-border .a-spacing-base')
                    for data in datas :
                        
                        image_url = data.select_one('img.s-image')['src']
                        link_of_product = 'https://www.amazon.ae' + data.select_one('a.a-link-normal.s-link-style.a-text-normal')['href']
                        title = data.select_one(' a.a-link-normal.s-line-clamp-4.s-link-style.a-text-normal').text.strip()
                    
                        con = data.select_one(' div.a-row.a-size-base.a-color-base div.a-row').text
                
                        matches = re.findall(r'AED\s*([\d,]+(?:\.\d+)?)', con)
                        
                        discounted_price = None
                        real_price = None
                        discount_percentage = None
                        if len(matches) >= 1:
                            s = matches[0].replace(',', '')
                            discounted_price = int(float(s))
                        if len(matches) >= 3:
                            s = matches[2].replace(',', '')
                            real_price = int(float(s))
                        if discounted_price is not None and real_price is not None and real_price != 0:
                            discount_percentage = int(100 - ((discounted_price / real_price) * 100))
                            if (discount_percentage > 30) and real_price and real_price > 100:
                                print(f'{title} - {discount_percentage}%')
                                # Save to MySQL database
                                try:
                                    product = Product(
                                        image_url=image_url,
                                        link_of_product=link_of_product,
                                        title=title,
                                        real_price=real_price,
                                        discounted_price=discounted_price,
                                        discount_percentage=discount_percentage
                                    )
                                    db.add(product)
                                    db.commit()
                                except Exception as e:
                                    print(f"Error saving to database: {e}")
                                    db.rollback()
                except AttributeError :
                    pass
                                  
                try:        
                    c = page.locator(' .s-pagination-next')
                    # Check if the button is disabled (reached last page)
                    is_disabled = c.get_attribute('aria-disabled')
                    if is_disabled == 'true':
                        print("Reached last page, moving to next link...")
                        break
                    c.click()
                    time.sleep(1)
                except  :
                    break
                    
    
        elif link.strip() and 'https://www.namshi.com' in link:
            
            try:
                print(f"Processing namshy link: {link.strip()}")
                page.goto(link , timeout=30000 , wait_until='load')
                time.sleep(5)
                page.get_by_role("button", name="قبول").click()
                page.wait_for_load_state('domcontentloaded')
            except Exception as e:
                print(f"Error loading namshy page: {e}")
                continue
            while True:
                try:
                    # Use safe scrolling function
                    if not safe_scroll_page(page):
                        time.sleep(5)
                        if not safe_scroll_page(page):
                            print("Scrolling failed, moving to next link...")
                            break
                        
                    soup = bs4.BeautifulSoup(page.content(), "html.parser")
                    
                    datas = soup.select('.ProductBox_container__wiajf ')
                    for data in datas :
                        
                        try:
                            title = data.select_one('.ProductBox_brand__oDc9f').text
                            image_url = data.select(' img')[1]['src']
                            link_of_product = 'https://www.namshi.com' + data.select('a')[0]['href']
                            real_price =int(float(str(data.select('.ProductPrice_preReductionPrice__S72wT ')[0].text.replace(',' , ''))))
                            discounted_price =int(float(str(data.select('.ProductPrice_value__hnFSS')[0].text.replace(',' , ''))))
                            discount_percentage = int(100 - ((discounted_price / real_price) * 100))
                        except IndexError :
                            continue
                            
                        if discounted_price is not None and real_price is not None and real_price != 0:
                            if (discount_percentage > 30) and real_price and real_price > 100:
                                print(f'{title} - {discount_percentage}%')
                                # Save to MySQL database
                                try:
                                    product = Product(
                                        image_url=image_url,
                                        link_of_product=link_of_product,
                                        title=title,
                                        real_price=real_price,
                                        discounted_price=discounted_price,
                                        discount_percentage=discount_percentage
                                    )
                                    db.add(product)
                                    db.commit()
                                except Exception as e:
                                    print(f"Error saving to database: {e}")
                                    db.rollback()
                except AttributeError :
                    pass
                                    
                try: 
                    # Try different pagination selectors for Namshi
                    c = page.get_by_role("link", name="chevronForwardBold", exact=True)

                    
                    # If no pagination element found, we're done
                    if not c.count():
                        print("No pagination found, moving to next link...")
                        break
     
                    # Check if the button is disabled (reached last page)
                    try:
                        is_disabled = c.get_attribute('aria-disabled')
                        if is_disabled == 'true':
                            print("Reached last page, moving to next link...")
                            break
                        c.click()
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error clicking pagination: {e}")
                        break
                except  :
                    break
                    
        elif link.strip() and 'https://www.noon.com' in link:
            try:
                print(f"Processing Noon link: {link.strip()}")
                page.goto(link , timeout=30000 , wait_until='load')
                page.wait_for_load_state('domcontentloaded')
            except Exception as e:
                print(f"Error loading Noon page: {e}")
                continue
            while True:
                try:
                    # Use safe scrolling function
                    if not safe_scroll_page(page):
                        time.sleep(5)
                        if not safe_scroll_page(page):
                            print("Scrolling failed, moving to next link...")
                            break
                        
                    soup = bs4.BeautifulSoup(page.content(), "html.parser")
                   
                    datas = soup.select('.ProductBoxLinkHandler_linkWrapper__b0qZ9 ')
                    for data in datas :
                        title = data.select_one('.ProductDetailsSection_title__JorAV').text
                        try:
                            image_url = data.select(' img')[1]['src']
                            link_of_product = 'https://www.noon.com' + data.select('a')[0]['href']
                            real_price =int(float(str(data.select('.Price_oldPrice__ZqD8B')[0].text.replace(',' , ''))))
                            discounted_price =int(float(str(data.select('.Price_amount__2sXa7')[0].text.replace(',' , ''))))
                            discount_percentage = int(100 - ((discounted_price / real_price) * 100))
                        except IndexError :
                            continue
                            
                        if discounted_price is not None and real_price is not None and real_price != 0:
                            if (discount_percentage > 30) and real_price and real_price > 100:
                                print(f'{title} - {discount_percentage}%')
                                # Save to MySQL database
                                try:
                                    product = Product(
                                        image_url=image_url,
                                        link_of_product=link_of_product,
                                        title=title,
                                        real_price=real_price,
                                        discounted_price=discounted_price,
                                        discount_percentage=discount_percentage
                                    )
                                    db.add(product)
                                    db.commit()
                                except Exception as e:
                                    print(f"Error saving to database: {e}")
                                    db.rollback()
                except AttributeError :
                    pass
                                  
                try:        
                    c = page.locator(' .next .PlpPagination_arrowLink__QSqKF')
                    # Check if the button is disabled (reached last page)
                    is_disabled = c.get_attribute('aria-disabled')
                    if is_disabled == 'true':
                        print("Reached last page, moving to next link...")
                        break
                    c.click()
                    time.sleep(1)
                except  :
                    break
                    
                
    db.close()
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
