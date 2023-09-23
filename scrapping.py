from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import re
import requests, time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pyautogui

def scroll_down(driver):
    scroll_height = 0
    prev_scroll_height = 0
    while 1:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        if scroll_height == prev_scroll_height:
            break
        prev_scroll_height = scroll_height

def scrapp_website(url,xpath):
    path = "driver/chromedriver.exe"
    binary_path = "driver/chrome-test/chrome.exe"
    chrome_options = Options()
    chrome_options.binary_location = binary_path
    chrome_service = Service(executable_path=path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 2) 
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    scroll_down(driver)
    html_content = driver.find_element(By.TAG_NAME, "body")
    body = html_content.get_attribute("innerHTML")
    driver.quit()
    emails = set()
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    for match in re.finditer(pattern, body):
        emails.add(match.group())
    return emails

def remove_first(input_text,html_input):
    first_part=html_input.find(input_text)
    if first_part == -1:
            return 'Not Found'
    else:
        html_input = html_input[first_part:]
        html_input = html_input.replace(input_text,'')
        return html_input

def split(splits):
    y = '.'
    result = []
    for i in range(len(splits),0,-1):
        array = []
        first_array = splits[:i]
        second_array = splits[i:]
        array.append(y.join(first_array))
        array.append(second_array)
        result.append(array)
    return result

def replace_all(splits,html_input):
    keywords = split(splits)
    for keyword in keywords:
        find_keyword=html_input.find(keyword[0])
        if find_keyword != -1:
            html_input = html_input.replace(keyword[0],'(\w+)')
            if len(keyword[1])!=0:
                html_input = replace_all(keyword[1],html_input)
            return html_input
    return html_input

def scrapp_deep(url,wanted_email,html_input,xpath):
    wanted_email = wanted_email.split('@')
    first_part = wanted_email[0]
    second_part = wanted_email[1]
    html_input = html_input.replace(" ", "")
    html_input = html_input.replace("\n", "")
    second_part = second_part.split('.')
    html_input = remove_first(first_part, html_input)
    html_input = replace_all(second_part, html_input)
    markers = html_input.split('(\w+)')
    path = "driver/chromedriver.exe"
    binary_path = "driver/chrome-test/chrome.exe"
    chrome_options = Options()
    chrome_options.binary_location = binary_path
    chrome_service = Service(executable_path=path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 5) 
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        pass
    scroll_down(driver)
    html_content = driver.find_element(By.TAG_NAME, "body")
    body = html_content.get_attribute("innerHTML")
    driver.quit()
    emails = set()
    body = body.replace(" ", "")
    body = body.replace("\n", "")
    body = body.replace(markers[0], '@')
    for i in range(1,len(markers)-1):
        body = body.replace(markers[i], '.')
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    for match in re.finditer(pattern, body):
        emails.add(match.group())
    return emails

def scrapp_advanced(markers,body):
    body = body.replace(" ", "")
    body = body.replace("\n", "")
    body = body.replace(markers[0], '@')
    emails = set()
    for i in range(1,len(markers)-1):
        body = body.replace(markers[i], '.')
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    for match in re.finditer(pattern, body):
        emails.add(match.group())
    return emails

def scrapp(body):
    emails = set()
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    for match in re.finditer(pattern, body):
        emails.add(match.group())
    return emails

def loading(driver,action):
    try:
        wait = WebDriverWait(driver, 5) 
        wait.until(EC.presence_of_element_located((By.XPATH, action)))
        element = driver.find_element(By.XPATH, action)
        if element.is_enabled() and element != None:
            element.click()
            time.sleep(3)
            return True
        else:
            return False
    except:
        return False

def scrapp_normal_action(url,actionTypeInput,actionInput,xpath):
    path = "driver/chromedriver.exe"
    binary_path = "driver/chrome-test/chrome.exe"
    chrome_options = Options()
    chrome_options.binary_location = binary_path
    chrome_service = Service(executable_path=path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 5) 
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    scroll_down(driver)
    i = 0
    emails = set()
    if actionTypeInput == 'click':
        for action in actionInput:
            n=-1
            if action.endswith(')'):
                j = action.rfind('(')
                if j != -1:
                    n = action[j+1:-1]
                    n = int(n)
                    action = action[:j]
            while n != 0:
                if n>0:
                    n=n-1
                try:
                    scroll_down(driver)
                    html_content = driver.find_element(By.TAG_NAME, "body")
                    result = scrapp(html_content.get_attribute("innerHTML"))
                    for email in result:
                        emails.add(email)
                    elementExist = loading(driver,action)
                    if not elementExist:
                        break
                except:
                    break
    elif actionTypeInput == 'links':
        for action in actionInput:
            try:
                elements = driver.find_elements(By.XPATH, action)
                for element in elements:
                    link_branch = element.get_attribute("href")
                    result = scrapp_website(link_branch,'//body')
                    for email in result:
                        emails.add(email)
            except:
                break
    elif actionTypeInput == 'links-click' :
        seperatingLinksClick = actionInput.index('////')
        try:
            links = actionInput[:seperatingLinksClick]
            clicks = actionInput[seperatingLinksClick+1:]
        except:
            return []
        for click in clicks:
            n=-1
            if click.endswith(')'):
                j = click.rfind('(')
                if j != -1:
                    n = click[j+1:-1]
                    n = int(n)
                    click = click[:j]
            while n != 0:
                if n>0:
                    n=n-1
                try:
                    scroll_down(driver)
                    html_content = driver.find_element(By.TAG_NAME, "body")
                    for link in links:
                        elements = driver.find_elements(By.XPATH, link)
                        for element in elements:
                            link_branch = element.get_attribute("href")
                            result = scrapp_website(link_branch,'//body')
                            for email in result:
                                emails.add(email)
                    elements = driver.find_element(By.XPATH, click)
                    elementExist = loading(driver,action)
                    if not elementExist:
                        break
                except:
                    break
    time.sleep(2)
    return emails
    
def scrapp_deep_action(url,actionTypeInput,actionInput,emailInput,htmlInput,xpathInput):
    emailInput = emailInput.split('@')
    first_part = emailInput[0]
    second_part = emailInput[1]
    htmlInput = htmlInput.replace(" ", "")
    htmlInput = htmlInput.replace("\n", "")
    second_part = second_part.split('.')
    htmlInput = remove_first(first_part, htmlInput)
    htmlInput = replace_all(second_part, htmlInput)
    markers = htmlInput.split('(\w+)')
    path = "driver/chromedriver.exe"
    binary_path = "driver/chrome-test/chrome.exe"
    chrome_options = Options()
    chrome_options.binary_location = binary_path
    chrome_service = Service(executable_path=path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 5) 
    wait.until(EC.presence_of_element_located((By.XPATH, xpathInput)))
    scroll_down(driver)
    i = 0
    emails = set()
    if actionTypeInput == 'load' or actionTypeInput == 'next':
        for action in actionInput:
            n=-1
            if action.endswith(')'):
                j = action.rfind('(')
                if j != -1:
                    n = action[j+1:-1]
                    n = int(n)
                    action = action[:j]
            while n != 0:
                if n>0:
                    n=n-1
                try:
                    html_content = driver.find_element(By.TAG_NAME, "body")
                    result = scrapp_advanced(markers,html_content.get_attribute("innerHTML"))
                    for email in result:
                        emails.add(email)
                    elementExist = loading(driver,action)
                    if not elementExist:
                        break
                except:
                    break
    elif actionTypeInput == 'links':
        for action in actionInput:
            try:
                elements = driver.find_elements(By.XPATH, action)
                for element in elements:
                    link_branch = element.get_attribute("href")
                    result = scrapp_deep(link_branch,emailInput,htmlInput,'//body')
                    for email in result:
                        emails.add(email)
            except:
                break
    elif actionTypeInput == 'links-load' or actionTypeInput == 'links-next':
        seperatingLinksClick = actionInput.index('////')
        try:
            links = actionInput[:seperatingLinksClick]
            clicks = actionInput[seperatingLinksClick+1:]
        except:
            return []
        for click in clicks:
            n=-1
            if click.endswith(')'):
                j = click.rfind('(')
                if j != -1:
                    n = click[j+1:-1]
                    n = int(n)
                    click = click[:j]
            while n != 0:
                if n>0:
                    n=n-1
                try:
                    scroll_down(driver)
                    html_content = driver.find_element(By.TAG_NAME, "body")
                    for link in links:
                        elements = driver.find_elements(By.XPATH, link)
                        for element in elements:
                            link_branch = element.get_attribute("href")
                            result = scrapp_deep(link_branch,emailInput,htmlInput,'//body')
                            for email in result:
                                emails.add(email)
                    elements = driver.find_element(By.XPATH, click)
                    elementExist = loading(driver,action)
                    if not elementExist:
                        break
                except:
                    break
    return emails
