from analyzer import Analyzer
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse and validate a path.")
    parser.add_argument('path', type=str, help="The path to be parsed and validated.")
    args = parser.parse_args()
    Analyzer(*args)()

