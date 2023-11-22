import game_structures as gm
import json

tester = gm.Game(name = 'test')

a_dict = {'name': 'slay', 'gorely_opinion':{'complexity':[3]}}
another_dict = {'name': 'beep', 'gorely_opinion':{'complexity':[3, 7]}}

a_list = [a_dict, another_dict]
#with open('test_2.json', 'w') as outfile:
     #json.dump(a_list, outfile, indent=2)

#loaded = gm.GameInventory.load_game_inventory(a_list)
#loaded.save('test')

test = gm.GameInventory.load_game_inventory('game_inventory.json')
print(test)

