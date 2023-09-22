from scrapping import *


def pick_scrapping_method(url,emailInput,htmlInput,actionTypeInput,actionInput):
    if actionInput.replace(' ','') == '' or actionTypeInput == '':
        if htmlInput.replace(' ', '') == '' or emailInput.replace(' ', '')=="":
            return scrapp_website(url,'//body')
        else:
            return scrapp_deep(url,emailInput,htmlInput,'//body')
    else:
        actionInput = actionInput.split('\n')
        actionInput = [action.replace(' ','') for action in actionInput]
        actionInput = [action.replace('\r','') for action in actionInput]
        actionInput = [action for action in actionInput if action.startswith('//')]
        if htmlInput.replace(' ', '') == '' or emailInput.replace(' ', '')=='':
            return scrapp_normal_action(url,actionTypeInput,actionInput,'//body')
        else:
            return scrapp_deep_action(url,actionTypeInput,actionInput,emailInput,htmlInput,'//body')
