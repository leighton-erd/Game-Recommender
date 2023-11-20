from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import game_structures as gm


driver = webdriver.Chrome()
initial_dict = {'age_rec': '//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item", " " )) and (((count(preceding-sibling::*) + 1) = 3) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item-primary", " " ))]',
                 'game_release_date': '//*[contains(concat( " ", @class, " " ), concat( " ", "game-year", " " ))]',
                 'players':'//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item-primary", " " ))]',
                 'BGG_rating':'//*[contains(concat( " ", @class, " " ), concat( " ", "has-rating-7", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "ng-binding", " " ))]',
                 'BGG_age_rec':'//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item", " " )) and (((count(preceding-sibling::*) + 1) = 3) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "btn-xs", " " ))]',
                 'BGG_rating_num':'//*[contains(concat( " ", @class, " " ), concat( " ", "game-header-title-summary", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "ng-binding", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]',
                 'BGG_optimum_players':'//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "btn-xs", " " ))]',
                 'BGG_average_playing_time':'//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-item-primary", " " ))]',
                 'BGG_complexity':'//*[contains(concat( " ", @class, " " ), concat( " ", "gameplay-weight-light", " " ))]',
                 'BGG_description':'//p[contains(concat( " ", @class, " " ), concat( " ", "ng-scope", " " ))]',
                 'themes':'//*[contains(concat( " ", @class, " " ), concat( " ", "ng-scope", " " )) and (((count(preceding-sibling::*) + 1) = 4) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-block", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "ng-binding", " " ))]',
                 'mechanisms':'//*[contains(concat( " ", @class, " " ), concat( " ", "ng-scope", " " )) and (((count(preceding-sibling::*) + 1) = 3) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "text-block", " " ))]'
}


def retrieve_raw_information(a_driver, x_path: str):
    try:
        response = a_driver.find_elements(By.XPATH, x_path)
    except:
        response = None
        return response
    else:
        res_list: list = []
        for a in response:
            res_list.append(a.text)
        if len(res_list) == 1:
            return res_list[0]
        else:
            return res_list


def reformulate_single_num(num_str: str):
    if num_str != None:
        return int(re.findall(r'\d+', num_str)[0])
    else:
        return None

def reformulate_boundary(boundary_str:str):
    if boundary_str != None:
        all_nums = re.findall(r'\d+', boundary_str)
        return (int(all_nums[0]), int(all_nums[1]))
    else:
        return None

def boundary_average(boundary_str: str):
    if boundary_str != None:
        boundary_tuple = reformulate_boundary(boundary_str)
        return sum(boundary_tuple)/len(boundary_tuple)
    else:
        return None

def reformulate_theme_list(list_str: str):
    if list_str != None:
        as_list = []
        for description in list_str:
            if 'Theme' in description:
                theme_name, theme = description.split(':')
                as_list.append(theme.strip())
        return as_list

def reformulate_mechanisms(mechanism_str: str):
    if mechanism_str != None:
        return [a for a in mechanism_str if '+' not in a]

def reformulate_optimum_players(player_str: str):
    if player_str != None:
        actual, optimum = player_str.split('—')
        return int(re.findall(r'\d+', optimum)[0])
    
def floatify(a_str: str):
    if a_str != None: 
        return float(a_str)
   
def reformulate_response(old_dict:dict):
    
    response_dict = old_dict.copy()
    response_dict['age_rec'] = reformulate_single_num(response_dict['age_rec'])
    response_dict['game_release_date'] = reformulate_single_num(response_dict['game_release_date'])
    response_dict['players'] = reformulate_boundary(response_dict['players'])

    response_dict['BGG_rating'] = floatify(response_dict['BGG_rating'])
    response_dict['BGG_age_rec'] = reformulate_single_num(response_dict['BGG_age_rec'])
    response_dict['BGG_rating_num'] = reformulate_single_num(response_dict['BGG_rating_num'])*1000
    response_dict['BGG_optimum_players'] = reformulate_optimum_players(response_dict['BGG_optimum_players'])
    response_dict['BGG_average_playing_time'] = boundary_average(response_dict['BGG_average_playing_time'])
    response_dict['BGG_complexity'] = floatify(response_dict['BGG_complexity'])
    response_dict['themes'] = reformulate_theme_list(response_dict['themes'])
    response_dict['mechanisms'] = reformulate_mechanisms(response_dict['mechanisms'])

    return response_dict

def get_information_for_game(game_name:str, game_url: str, a_driver = driver, x_path_dict:dict = initial_dict):
    a_driver.get(game_url)
    response_dict = {}
    for key, xpath_url in x_path_dict.items():
        web_response = retrieve_raw_information(a_driver, xpath_url)
        response_dict[key] = web_response
    formatted_dict = reformulate_response(response_dict)
    response_model = gm.Game(name = game_name, **formatted_dict)
    return response_model