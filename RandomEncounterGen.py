import argparse
import json
import pandas as pd
import sys
from pprint import pprint

DIFFICULTIES = ["Easy", "Medium", "Hard", "Deadly"]

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

    print_break()

    return args


def main():
    args = arg_parse()
    show_settings(args)

    args = character_xp_calc(args)
    
    monster_man_df = pd.read_csv("Data/monster_manual.csv")


if __name__ == '__main__':
    main()