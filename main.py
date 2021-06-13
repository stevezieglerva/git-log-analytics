import argparse
import os
import sys

import analyze_git_csv
import git_log_to_csv

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        type=str,
        help="filename of the csv logfile",
    )
    parser.add_argument(
        "--exclude_file_pattern",
        type=str,
        help="pattern of files to exclude",
        default="\.gem|\.lock|yarn|gemfile",
    )
    parser.add_argument(
        "--exclude_author_pattern",
        type=str,
        help="pattern of authors to exclude",
        default="dependabot|github",
    )

    args = parser.parse_args()

    filename_path = os.path.dirname(args.filename)
    source_abs_path = os.path.abspath(filename_path)
    print(source_abs_path)

    git_log_to_csv.create_csv(
        args.filename, args.exclude_file_pattern, args.exclude_author_pattern
    )
    analyze_git_csv.do_analysis("output/git_log.csv", source_abs_path)
