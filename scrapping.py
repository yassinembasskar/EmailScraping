from selenium.webdriver.common.by import By
from selenium import webdriver
import re
import requests


'''
not successful website to scrapp:
---------------------------------


=====>  https://www.ucm.es/teorica/staff  (you should auto complete the emails) very hard to solve but possible for the interface


=====> https://www.uic.es/en/contacts-directory (the problem is that you should click a button to see all the emails it gives you a limited number of emails) (load more button)
       http://anatomi.medicine.ankara.edu.tr/en/academic-staff/ (the same as previous but) (the next and previous buttons)
       https://stanfordwho.stanford.edu/people (the same as previous but) (infinite scroll to loadMore())

=====> https://www.cs.washington.edu/people/staff (the seperator is an image and a js function is generated when opening the website so this is really very special case) cannot be solved very very hard
 (not secure) cannot be solved


solved problems and now can ve scrapped:
---------------------------------------

https://research-information.bris.ac.uk/en/persons/ (seperating email format) solved in scrapp_again()
<a data-md5="bWFpbHRvOm5hMTQ0ODNAYnJpc3RvbC5hYy51aw==" href="#" class="email" tabindex="-1">na14483<span class="email-ta">@</span><script>encryptedA();</script>bristol.ac<span class="email-tod">.</span><script>encryptedDot();</script>uk</a>
na14483@bristol.ac.uk

very easy to scrapp websites:
-----------------------------

http://www.aui.ma/en/sba/2-aui-pages/2224-aui-contact-us.html
https://gsehd.gwu.edu/directory (this is a good website)
https://www.birmingham.ac.uk/research/metabolism-systems/staff/a-z-staff-list.aspx
https://www.birmingham.ac.uk/schools/education/staff/index.aspx
https://www.ed.ac.uk/education/about-us/people/academic-staff-a-z
https://www.gse.harvard.edu/directory
http://www.narg.org.uk/people-and-partners/staff-directory/ (not secure but good)

'''

def scrapp_website(url):
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        driver.implicitly_wait(10)
        html_content = driver.find_element(By.TAG_NAME, "body")
        body = html_content.get_attribute("innerHTML")
        driver.quit()
    except:
        body = 'failed'
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

def scrapp_again(url,wanted_email,html_input):
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
    driver.implicitly_wait(30)
    driver.get(url)
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