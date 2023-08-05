from scrapping import *


def pick_scrapping_method(url,emailInput,htmlInput,xpathInput,actionTypeInput,actionInput):
    if actionInput.replace(' ','') == '' or actionTypeInput == '':
        if xpathInput.replace(' ','') == '':
            if htmlInput.replace(' ', '') == '' or emailInput.replace(' ', ''):
                return []
            else:
                return scrapp_deep(url,emailInput,htmlInput,'//body')
        else:
            if htmlInput.replace(' ', '') == '' or emailInput.replace(' ', ''):
                return scrapp_website(url,xpathInput)
            else:
                return scrapp_deep(url,emailInput,htmlInput,xpathInput)
    else:
        actionInput = actionInput.split('\n')
        actionInput = [action.replace(' ','') for action in actionInput]
        actionInput = [action.replace('\r','') for action in actionInput]
        actionInput = [action for action in actionInput if action.startswith('//')]
        if xpathInput.replace(' ','') == '':
            if htmlInput.replace(' ', '') == '' or emailInput.replace(' ', ''):
                return scrapp_normal_action(url,actionTypeInput,actionInput,'//body')
            else:
                return scrapp_deep_action(url,actionTypeInput,actionInput,emailInput,htmlInput,'//body')
        else:
            if htmlInput.replace(' ', '') == '' or emailInput.replace(' ', ''):
                return scrapp_normal_action(url,actionTypeInput,actionInput,xpathInput)
            else:
                return scrapp_deep_action(url,actionTypeInput,actionInput,emailInput,htmlInput,xpathInput)



'''actions = action_input
        actions = actions.split(' ')
        howto = []
        identifications = []
        for action in actions:
            if action.startswith('(links)'):
                howto.append('links')   
            elif action.startswith('(click)'):
                    howto.append('click')
            else:
                break
            action = action[7:]
            if action.startswith('//'):
                identifications.append(action)
            else:
                break'''