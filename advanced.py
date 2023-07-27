from scrapping import *


def pick_scrapping_method(url,email_input,html_input,xpath_input,action_input):
    if action_input.replace(' ','') == '':
        if xpath_input.replace(' ','') == '':
            if html_input.replace(' ', '') == '' or email_input.replace(' ', ''):
                return []
            else:
                return scrapp_deep(url,email_input,html_input,'//body')
        else:
            if html_input.replace(' ', '') == '' or email_input.replace(' ', ''):
                return scrapp_website(url,xpath_input)
            else:
                return scrapp_deep(url,email_input,html_input,xpath_input)
    else:
        actions = action_input
        actions = actions.split(' ')
        howto = []
        identifications = []
        for action in actions:
            if action.startswith('(links)'):
                howto.append('(links)')   
            elif action.startswith('(click)'):
                    howto.append('click')
            else:
                break
            action = action[7:]
            if action.startswith('//'):
                identifications.append(action)
            else:
                break
        if xpath_input.replace(' ','') == '':
            if html_input.replace(' ', '') == '' or email_input.replace(' ', ''):
                return scrapp_normal_action(url,howto,identifications,'//body')
            else:
                return scrapp_deep_action(url,howto,identifications,email_input,html_input,'//body')
        else:
            if html_input.replace(' ', '') == '' or email_input.replace(' ', ''):
                return scrapp_normal_action(url,howto,identifications,xpath_input)
            else:
                return scrapp_deep_action(url,howto,identifications,email_input,html_input,xpath_input)

action_input = '(click)//*[@id="block-mithr-theme-mithr-theme-system-main"]/div/div/div/ul/li/a'
url = 'https://hr.mit.edu/staff'