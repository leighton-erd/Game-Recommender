from pydantic import BaseModel as bm
from typing import Optional, Any, Type
import json

class gorely_stats(bm):
    real_ratings: Optional[list[tuple[int, float]]] = []
    playing_times:Optional[list[tuple[int, float]]] = []

    complexity:Optional[list[float]] = []
    age_rec:Optional[list[int]] = []

    def gorely_rating_average(self):
        all_ratings = [ratings_pair[1] for ratings_pair in self.real_ratings]
        if len(all_ratings) != 0:
            return round((sum(all_ratings)/len(all_ratings)), 2)
        else:
            return None
    
    def gorely_player_average(self, num_of_players:int):
        player_ratings = [ratings_pair[1] for ratings_pair in self.playing_times if ratings_pair[0] == num_of_players]
        if len(player_ratings) != 0:
            return round((sum(player_ratings)/len(player_ratings)), 2)
        else:
            return None
        
    def gorely_time_average(self):
        all_ratings = [ratings_pair[1] for ratings_pair in self.real_ratings]
        if len(all_ratings) != 0:
            return round((sum(all_ratings)/len(all_ratings)))
        else:
            return None
    
    def gorely_time_player_average(self, num_of_players:int):
        player_ratings = [ratings_pair[1] for ratings_pair in self.playing_times if ratings_pair[0] == num_of_players]
        if len(player_ratings) != 0:
            return round((sum(player_ratings)/len(player_ratings)))
        else:
            return None
    
    def gorely_complexity(self):
        comp_rating = self.complexity
        if len(comp_rating) != 0:
            return round((sum(comp_rating)/len(comp_rating)), 2)
        else:
            return None
        
    def gorely_complexity(self):
        comp_rating = self.age_rec
        if len(comp_rating) != 0:
            return round((sum(comp_rating)/len(comp_rating)))
        else:
            return None


class Game(bm):
    name: str
    age_rec: Optional[int] = 0
    game_release_date: Optional[int] = 0
    players: Optional[tuple[int, int]] = (0,0)

    BGG_rating: Optional[float] = None
    BGG_age_rec: Optional[int] = None
    BGG_rating_num: Optional[int] = None
    BGG_optimum_players: Optional[int] = None
    BGG_average_playing_time: Optional[int] = None
    BGG_complexity: Optional[float] = None
    BGG_description: Optional[str] = None
    
    themes: Optional[list[str]] = None
    mechanisms: Optional[list[str]] = None

    gorely_opinion: Optional[gorely_stats] = gorely_stats()

    def append_a_rating(self, rating: float, num_of_players: int):
        rating_tuple = (num_of_players, rating)
        self.gorely_opinion.real_ratings.append(rating_tuple)

    def append_playing_time(self, rating: float, num_of_players: int):
        rating_tuple = (num_of_players, rating)
        self.gorely_opinion.playing_times.append(rating_tuple)

    def append_complexity(self, rating: float):
        self.gorely_opinion.complexity.append(rating)

    def append_age_rec(self, rating: float):
        self.gorely_opinion.age_rec.append(rating)

    @classmethod
    def from_dict(cls, game_dict: dict):
        return cls(**game_dict)



class GameInventory(bm):
    all_games: Optional[list[Game]] = []
    
    def add_game(self, a_game: Game):
        self.all_games.append(a_game)

    def find_games_requiring_manual_info(self):
        empty_games = []
        for each_game in self.all_games:
            if each_game.age_rec == 0 or each_game.game_release_date == 0 or each_game.players == (0,0):
                print(each_game.name)
                empty_games.append(each_game)
        return empty_games
    
    def save(self, save_name: str):
        formatted_list = [one_game.model_dump_json(indent = 5) for one_game in self.all_games]
        
        with open(f"{save_name}.json", "w") as outfile:
            json.dump(formatted_list, outfile, indent = 5)
    

    @classmethod
    def load_game_inventory(cls, file_path: str):
        with open(file_path) as user_file:
            game_list = json.load(user_file)

        new_inventory = cls()
        for each_game_dict in game_list:
            as_Game = Game.from_dict(eval(each_game_dict))
            new_inventory.all_games.append(as_Game)
        return new_inventory
        


