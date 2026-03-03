import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


if len(sys.argv) < 2:
    print("Usage: python test2.py <url>")
    sys.exit()

url = sys.argv[1]
if not url.startswith("http"):
    url = "https://" + url


options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--log-level=3") 

driver = webdriver.Chrome(options=options)



try:
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

   
    raw_text = driver.execute_script("""
        const noise = 'nav, footer, script, style, noscript, header, .menu, .sidebar, .social-links';
        document.querySelectorAll(noise).forEach(el => el.remove());
        return document.body.innerText;
    """)
    print("="*15 + "TITLE" + "="*15)
    print(f"TITLE: {driver.title.strip()}")
    print("-" * 30)

    seen_lines = set()
    print("="*15 + "BODY" + "="*15)
    for block in raw_text.split('\n'):
        block = block.strip()
        
        
        sentences = re.split(r'(?<=[.!?]) +', block)
        
        for sentence in sentences:
            clean_s = sentence.strip()
            
            
            if len(clean_s) < 5: 
                continue 
            
            if clean_s.lower() in seen_lines: 
                continue 
            
            print(clean_s)
            seen_lines.add(clean_s.lower())

    print("-" * 30)

    
    links = driver.find_elements(By.TAG_NAME, "a")
    unique_links = set()

    for link in links:
        href = link.get_attribute("href")
        if href and href.startswith("http"):
            clean_url = href.split('#')[0].rstrip('/')
            if clean_url:
                unique_links.add(clean_url)

    print(f"FOUND {len(unique_links)} UNIQUE LINKS:")
    print("="*15 + "LINK" + "="*15)
    for link in sorted(unique_links):
        print(link)

finally:
    driver.quit()