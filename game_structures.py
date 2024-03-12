from pydantic import BaseModel as bm
from typing import Optional, Any, Type
import json
import pandas as pd
import numpy as np


######################################
def weighted_rating(
    bgg_rating: float,
    gorely_rating: float,
    gorely_player_rating: float,
    num_players: int,
    optimum_players: int,
):
    weights = []
    ratings = [bgg_rating]
    if num_players == optimum_players:
        weights.append(1.05)
    else:
        weights.append(1)

    if gorely_rating != 0:
        weights.append(1.5)
        ratings.append(gorely_rating)

    if gorely_player_rating != 0:
        weights.append(1.5)
        ratings.append(gorely_player_rating)

    new_rating = np.round(
        sum((np.array(weights) * np.array(ratings))) / sum(weights), 1
    )
    return new_rating


category_dict = {
    "short and sweet": (0, 30),
    "sit down gathering": (20, 75),
    "consume my mind": (75, 1000000000000),
    "welcome to boardgames": (0, 2.2),
    "ill dabble again": (2, 3),
    "consume my mind": (2.7, 5),
    "new": (2012, 3000),
    "classic": (2003, 2015),
    "old school": (1900, 2003),
    "popular": (10000, 100000000000),
    "cult fav": (10000, 30000),
    "hidden treasure": (0, 10000),
    "": (0, 1000000000000000000000),
}


class gorely_stats(bm):
    real_ratings: Optional[list[tuple[int, float]]] = []
    playing_times: Optional[list[tuple[int, float]]] = []

    complexity: Optional[list[float]] = []
    age_rec: Optional[list[int]] = []

    def gorely_rating_average(self):
        all_ratings = [ratings_pair[1] for ratings_pair in self.real_ratings]
        if len(all_ratings) != 0:
            return round((sum(all_ratings) / len(all_ratings)), 2)
        else:
            return 0

    def gorely_player_average(self, num_of_players: int):
        player_ratings = [
            ratings_pair[1]
            for ratings_pair in self.playing_times
            if ratings_pair[0] == num_of_players
        ]
        if len(player_ratings) != 0:
            return round((sum(player_ratings) / len(player_ratings)), 2)
        else:
            return 0


class Game(bm):
    name: str
    age_rec: Optional[int] = 0
    game_release_date: Optional[int] = 0
    players: Optional[tuple[int, int]] = (0, 0)

    BGG_rating: Optional[float] = 0.0
    BGG_age_rec: Optional[int] = 0
    BGG_rating_num: Optional[int] = 0
    BGG_optimum_players: Optional[int] = 0
    BGG_average_playing_time: Optional[int] = 0
    BGG_complexity: Optional[float] = 0.0
    BGG_description: Optional[str] = None

    themes: Optional[list[str]] = []
    mechanisms: Optional[list[str]] = []

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

    def calc_weighted_rating(
        self,
        game_players: int,
        game_age: str = "",
        popularity: str = "",
        themes_mechanisms: list[str] = [],
    ):
        gorely_rating = self.gorely_opinion.gorely_rating_average()
        gorely_player_rating = self.gorely_opinion.gorely_player_average(
            num_of_players=game_players
        )

        initial_rating = weighted_rating(
            self.BGG_rating,
            gorely_rating,
            gorely_player_rating,
            game_players,
            self.BGG_optimum_players,
        )

        if game_age != "":
            boundary = category_dict[game_age]
            if boundary[0] <= self.game_release_date <= boundary[1]:
                initial_rating += 1
        if popularity != "":
            boundary = category_dict[popularity]
            if boundary[0] <= self.BGG_rating_num <= boundary[1]:
                initial_rating += 1
        contained_themes = [
            i for i in themes_mechanisms if i in self.themes or i in self.mechanisms
        ]
        if len(contained_themes) > 1:
            initial_rating += 1

        return initial_rating

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
            if (
                each_game.age_rec == 0
                or each_game.game_release_date == 0
                or each_game.players == (0, 0)
                or each_game.BGG_rating == None
            ):
                print(each_game.name)
                empty_games.append(each_game)
        return empty_games

    def get_game(self, game_name: str):
        for game in self.all_games:
            if game.name == game_name:
                return game

    def json_save(self, save_name: str):
        formatted_list = [
            one_game.model_dump_json(indent=5) for one_game in self.all_games
        ]

        with open(f"{save_name}.json", "w") as outfile:
            json.dump(formatted_list, outfile, indent=5)

    def csv_save(self, save_name: str):
        formatted_list = [one_game.model_dump() for one_game in self.all_games]
        as_frame = pd.DataFrame(formatted_list)
        as_frame.to_csv(f"{save_name}.csv", index=False)

    def filter_to_relevency(
        self, game_players: int, time: str = "", complexity: str = ""
    ):
        new_inventory = GameInventory()
        time_boundary = category_dict[time]
        complexity_boundary = category_dict[complexity]

        for one_game in self.all_games:
            if (
                one_game.players[0] <= game_players <= one_game.players[1]
                and time_boundary[0]
                <= one_game.BGG_average_playing_time
                <= time_boundary[1]
                and complexity_boundary[0]
                <= one_game.BGG_complexity
                <= complexity_boundary[1]
            ):
                new_inventory.add_game(one_game)
        return new_inventory

    def pair_games_with_weighted_ratings(
        self,
        game_players: int,
        time_vibe: str = "",
        game_age: str = "",
        popularity: str = "",
        complexity_vibe: str = "",
        themes_mechanisms: list = [],
    ):
        filtered_inventory = self.filter_to_relevency(
            game_players, time_vibe, complexity_vibe
        )
        trio_list = []
        for one_game in filtered_inventory.all_games:
            rating = one_game.calc_weighted_rating(
                game_players, game_age, popularity, themes_mechanisms
            )
            trio_list.append((one_game.name, one_game.BGG_description, rating))
        return trio_list
    

    def get_all_themes_and_mechanisms(self, save: bool = True, save_name: str = "themes_and_mechanisms"):
        all_games = self.all_games
        
        all_themes = [one_game.themes for one_game in all_games]
        all_mechanisms = [one_game.mechanisms for one_game in all_games]

        together = list(set([one_theme for theme_list in all_themes for one_theme in theme_list] + [one_mech for mech_list in all_mechanisms for one_mech in mech_list]))

        if save == True:
            with open(f"{save_name}.json", "w") as outfile:
                json.dump(together, outfile, indent=5)
        
        return together
    
    @classmethod
    def load_game_inventory(cls, file_path: str):
        with open(file_path) as user_file:
            game_list = json.load(user_file)

        new_inventory = cls()
        for each_game_dict in game_list:
            as_dict = json.loads(each_game_dict)
            as_Game = Game.from_dict(as_dict)
            new_inventory.all_games.append(as_Game)
        return new_inventory
