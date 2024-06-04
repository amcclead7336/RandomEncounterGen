import argparse
import pandas as pd


def arg_parse() -> argparse.Namespace:

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--strict', action='store_true', help='Returns results only with summited monsters')
    parser.add_argument('-m', '--monsters', nargs='+', help='Monsters to use in calculations')
    parser.add_argument('-c', '--characters', nargs='+', help='Character levels in encounter')
    parser.add_argument('-e', '--environments', nargs='+', help='environments to use in calculations')
    parser.add_argument('--max-size', help='Max number of enemies to return')
    parser.add_argument('--min-size', help='Min number of enemies to return')
    parser.add_argument('-j', '--json', help='Takes JSON as input')

    args = parser.parse_args()


    return args


def main():
    args = arg_parse()
    monster_man_df = pd.read_csv("Data/monster_manual.csv")


if __name__ == '__main__':
    main()