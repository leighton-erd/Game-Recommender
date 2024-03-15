import game_structures as gm
import recommender

game_inventory = gm.GameInventory.load_game_inventory('ready_made_games/game_inventory.json')
game_inventory.insert_rating('Gloomhaven', 5, 1, 40, 8)

recommender.recommend_a_game(game_inventory, 1)
