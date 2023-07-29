from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import re
import requests, time
from selenium.common.exceptions import NoSuchElementException

'''
not successful website to scrapp:
---------------------------------


=====>  https://www.ucm.es/teorica/staff  (you should auto complete the emails) very hard to solve but possible for the interface

====>http://anatomi.medicine.ankara.edu.tr/en/academic-staff/ 


solved problems and now can ve scrapped:
---------------------------------------

====> https://research-information.bris.ac.uk/en/persons/
      https://www.cs.washington.edu/people/staff (seperating email format) solved in scrapp_again()

====> https://stanfordwho.stanford.edu/people solved just by scrolling

very easy to scrapp websites:
-----------------------------

https://www.uic.es/en/contacts-directory
https://gsehd.gwu.edu/directory
http://www.aui.ma/en/sba/2-aui-pages/2224-aui-contact-us.html
https://www.birmingham.ac.uk/research/metabolism-systems/staff/a-z-staff-list.aspx
https://www.birmingham.ac.uk/schools/education/staff/index.aspx
https://www.ed.ac.uk/education/about-us/people/academic-staff-a-z
http://www.narg.org.uk/people-and-partners/staff-directory/
https://gostanford.com/staff-directory
https://macis.gess.ethz.ch/people.html
https://www.nus.edu.sg/celc/academic-staff-full-time/#administrative-staff
https://pennathletics.com/staff-directory
https://cornellrams.com/staff-directory?path=staff
https://leadersandbest.umich.edu/contact/directory
https://ecse.postech.ac.kr/member/professor/
'''
'''
testing websites:
================
loadMore: >>>>>DONE
--------
https://hr.mit.edu/staff    (successful)
https://www.cuchicago.edu/general-information/faculty-staff-directory/    (successful)
https://ischool.utoronto.ca/faculty-staff/faculty-staff-directory/       (successful)
https://www.ntu.edu.sg/newri/our-people/staff-directory#Content_C315_Col00

next: 
----
https://www.tudelft.nl/en/about-tu-delft/find-employees     (successful)
https://www.cambridgecollege.edu/faculty-and-staff/regional
https://www.lib.berkeley.edu/help/staff-directory
https://library.princeton.edu/staff/directory
https://www.rciti.unsw.edu.au/staff-directory
https://cbe.anu.edu.au/about/staff-directory

one email multi links:
----------------------
https://www.epfl.ch/research/faculty-members/     (this website is weird)
https://iis.fudan.edu.cn/en/faculty/list.htm
https://www.imperial.ac.uk/school-public-health/environmental-research-group/people/staff-directory/?
https://www.ucl.ac.uk/history/people/academic-staff
https://dso.college.harvard.edu/people/people-type/staff?page=2
https://www.conted.ox.ac.uk/profiles#?subject=&format=
https://www.unsw.edu.au/law-justice/about-us/our-people/staff-directory
https://www.sydney.edu.au/science/about/our-people/academic-staff.html
https://www.lse.ac.uk/economics/people/faculty

one email one link in multi links:
---------------------------------
https://english.yale.edu/people/faculty

combination of two:
------------------
https://publichealth.jhu.edu/faculty/directory/list?display_type=tablefaculty-members (multi links and incryptation)
https://www.ualberta.ca/science/programs/create/atums/team/u-of-a-students/index.html (encryptation and click)
https://www.kcl.ac.uk/people (next and multilinks)
https://research.monash.edu/en/persons/ (encryptation and next)

absolutely can not be scrapped:
------------------------------
https://www.polytechnique.edu/en/education/academic-and-research-departments/applied-mathematics-department-depmap/
'''
def scroll_down(driver):
    scroll_height = 0
    prev_scroll_height = 0
    while 1:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        if scroll_height == prev_scroll_height:
            break
        prev_scroll_height = scroll_height

def scrapp_website(url,xpath):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(3)
    try:
        wait = WebDriverWait(driver, 10) 
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        pass
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
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 10) 
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

def scrapp(body):
    emails = set()
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    for match in re.finditer(pattern, body):
        emails.add(match.group())
    return emails

def scrapp_normal_action(url,howto,identifications,xpath):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(2)
    wait = WebDriverWait(driver, 4) 
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    scroll_down(driver)
    i = 0
    emails = set()
    for how in howto:
        n=-1
        if identifications[i].endswith(')'):
            j = identifications[i].rfind('(')
            if j != -1:
                n = identifications[i][j+1:-1]
                n = int(n)
                identifications[i] = identifications[i][:j]
        time.sleep(2)
        if how == 'click':
            while n != 0:
                if n>0:
                    n=n-1
                try:
                    scroll_down(driver)
                    wait = WebDriverWait(driver, 10) 
                    wait.until(EC.presence_of_element_located((By.XPATH, identifications[i])))
                    element = driver.find_element(By.XPATH, identifications[i])
                    html_content = driver.find_element(By.TAG_NAME, "body")
                    result = scrapp(html_content.get_attribute("innerHTML"))
                    for email in result:
                        emails.add(email)
                    if not element.is_enabled():
                        break
                    element.click()
                    time.sleep(3)
                except:
                    break
        elif how == 'links':
            hasRange = False
            finPara = identifications[i].find(')')
            startPara = identifications[i].rfind('(')
            if (finPara != -1) and (startPara != -1):
                hasRange = True
                range_xpath = identifications[i][startPara+1:finPara]
                if range_xpath.find(':') == -1:
                    continue
                range_xpath = range_xpath.split(':')
                identifications[i] = identifications[i][:startPara+1]  + identifications[i][finPara:]
                x = range_xpath[0]
                y = range_xpath[1]
                try: 
                    x = int(x)
                except:
                    x = 1
                try: 
                    y = int(y)
                except:
                    y = None
            while n != 0:
                if n > 0:
                    n = n - 1
                try:
                    scroll_down(driver)
                    html_content = driver.find_element(By.TAG_NAME, "body")
                    result = scrapp(html_content.get_attribute("innerHTML"))
                    for email in result:
                        emails.add(email)
                    if hasRange:
                        if y != None:
                            for j in range(x,y):
                                try:
                                    time.sleep(2)
                                    element = driver.find_element(By.XPATH, identifications[i].replace('()',str(j)))
                                    link_branch = element.get_attribute("href")
                                    result = scrapp_website(link_branch,xpath)
                                    for email in result:
                                        emails.add(email)
                                    time.sleep(2)
                                except:
                                    break
                        else:
                            while 1:
                                try:
                                    time.sleep(2)
                                    element = driver.find_element(By.XPATH, identifications[i].replace('()',str(x)))
                                    link_branch = element.get_attribute("href")
                                    print(link_branch)
                                    result = scrapp_website(link_branch,'//body')
                                    print("hada ra9m "+ str(x))
                                    x+=1
                                    for email in result:
                                        emails.add(email)
                                    time.sleep(2)
                                except:
                                    break
                    else:
                        try:
                            time.sleep(2)
                            elements = driver.find_elements(By.XPATH, identifications[i])
                            for element in elements:
                                try:
                                    link_branch = element.get_attribute("href")
                                    result = scrapp_website(link_branch,'//body')
                                    for email in result:
                                        emails.add(email)
                                    time.sleep(2)
                                except:
                                    break
                        except:
                            pass
                except:
                    break
        else:
            break
        i+=1
    return emails
    
            