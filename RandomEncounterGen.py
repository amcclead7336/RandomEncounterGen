"""
This is a program that Generates an encounter based on parameters

Example Config_Template:
{
    "strict": true,
    "monsters": ["Goblin","Goblin Boss"],
    "characters": [1,1,2,2],
    "environments": ["Forest", "Hill"],
    "max-size":5,
    "min-size":4,
    "difficulty":"Medium"
}

"""

import argparse
import json
import pandas as pd
import sys
from pprint import pprint

DIFFICULTIES = ["Easy", "Medium", "Hard", "Deadly"]
ENVIRONMENTS = ["Arctic", "Coastal", "Desert", "Forest", "Grassland", 
                "Hill", "Mountain", "Swamp", "Underdark", "Underwater", 
                "Urban", "Other Plane"]

LOW_LEVEL_CUTOFF = 4

def arg_parse() -> argparse.Namespace:

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--strict', action='store_true', help='Returns results only with summited monsters')
    parser.add_argument('-m', '--monsters', nargs='+', help='Monsters to use in calculations', default=[])
    parser.add_argument('-c', '--characters', nargs='+', help='Character levels in encounter', default=[])
    parser.add_argument('-e', '--environments', nargs='+', help='environments to use in calculations', default=[])
    parser.add_argument('-d', '--difficulty', help='Difficulty level of the encounter: Default Medium', default="Medium")
    parser.add_argument('--max-size', help='Max number of enemies to return')
    parser.add_argument('--min-size', help='Min number of enemies to return')
    parser.add_argument('-j', '--json', help='Takes JSON as input, overwrites all other arguments')

    args = parser.parse_args()

    if args.json is not None:
        with open(args.json) as f:
            config = json.load(f)
        
        args.strict = config['strict']
        args.monsters = config['monsters']
        args.characters = config['characters']
        args.environments = config['environments']
        args.max_size = config['max-size']
        args.min_size = config['min-size']
        args.difficulty = config['difficulty']

        if args.difficulty not in DIFFICULTIES:
            print(f"Value for difficulty not expected, {args.difficulty}")
            sys.exit(1)
        
        return args
    
    if args.difficulty not in DIFFICULTIES:
        print(f"Value for difficulty not expected, {args.difficulty}")
        sys.exit(1)

    return args

def show_settings(args):
    print("Settings")
    for k, v in args.__dict__.items():
        print(f"{k: <15}:{str(v): >40}")
    
    print_break()


def print_break():
    print("============================================================================\n")


def character_xp_calc(args):

    with open("Data/threshold_table.json") as f:
        threshold_table = json.load(f)

    totals = [0, 0, 0, 0]
    
    for character in args.characters:
        level_thresholds = threshold_table[str(character)]
        for i, difficulty in enumerate(DIFFICULTIES):
            totals[i] += level_thresholds[difficulty]
    
    print("XP Calculations")
    for diff, tot in zip(DIFFICULTIES, totals):
        print(f"{diff: <15}:{tot: >40}")
        
    args.max_xp = totals[DIFFICULTIES.index(args.difficulty)]
    args.average_level = int(sum(args.characters)//len(args.characters))

    print_break()

    return args


def get_monster_options(monster_man_df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:

    current_mm_df = monster_man_df.copy()

    if min(args.characters) < LOW_LEVEL_CUTOFF:
        current_mm_df = monster_man_df[monster_man_df["CR_Clean"]<=int(args.average_level)]

    current_mm_df = current_mm_df[current_mm_df['CR_Clean']>0]

    if args.strict:
        if args.environments:
            current_mm_df = current_mm_df[(current_mm_df[args.environments]==1).any(axis=1)]

        if args.monsters:
            current_mm_df = current_mm_df[current_mm_df['Name'].isin(args.monsters)]

    return current_mm_df


def find_combinations(target_xp: int, monster_df: pd.DataFrame, current_combination=[], all_combinations=set()) -> set:
    # Base case: if target_xp is 0, we found a valid combination
    if target_xp == 0:
        # Sort the combination and convert to tuple to add to the set
        all_combinations.add(tuple(sorted(current_combination)))
        return all_combinations

    # If target_xp becomes negative, there is no valid combination
    if target_xp < 0:
        return all_combinations

    # Iterate over the DataFrame rows
    for i, monster in monster_df.iterrows():
        # Recur with the same DataFrame to allow multiple instances of the same monster
        find_combinations(target_xp - monster['XP'], monster_df, current_combination + [monster['Name']], all_combinations)

    return all_combinations


def string_to_float(x):
    if "/" in x:
        return int(x.split("/")[0])/int(x.split("/")[1])
    return x


def main():
    args = arg_parse()

    args = character_xp_calc(args)
    show_settings(args)
    
    monster_man_df = pd.read_csv("Data/monster_manual.csv")
    cr_to_xp_df = pd.read_csv("Data/CR_to_XP.csv")

    monster_man_df['CR_Clean'] = monster_man_df['CR'].apply(string_to_float).astype(float)
    monster_man_df = monster_man_df.merge(cr_to_xp_df, how="left", left_on="CR_Clean", right_on="CR").drop("CR_y",axis=1)

    monster_options_df = get_monster_options(monster_man_df, args)
    print(monster_options_df)
    print_break()

    pprint(find_combinations(args.max_xp, monster_options_df[["XP","Name"]]))
    print_break()


if __name__ == '__main__':
    main()