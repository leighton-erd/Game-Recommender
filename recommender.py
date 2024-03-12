import game_structures as gm

def recommend_a_game(
    inventory: gm.GameInventory,
    num_of_players: int,
    length_of_game: str = "",
    game_age: str = "",
    popularity: str = "",
    complexity_vibe: str = "",
    themes_mechanisms: list = [],
    num_of_recs: int = 3,
):
    relevent_games = inventory.pair_games_with_weighted_ratings(
        num_of_players,
        length_of_game,
        game_age,
        popularity,
        complexity_vibe,
        themes_mechanisms,
    )
    top = sorted(relevent_games, key=lambda tup: tup[2], reverse=True)[:num_of_recs]
    print(top)
