import sys
import os

import analyze_git_csv
import git_log_to_csv

if __name__ == "__main__":
    assert (
        len(sys.argv) == 2
    ), "Missing command line argument with the path of git log text file."

    filename = sys.argv[1]

    filename_path = os.path.dirname(filename)
    source_abs_path = os.path.abspath(filename_path)
    print(source_abs_path)

    git_log_to_csv.create_csv(filename)
    analyze_git_csv.do_analysis("output/git_log.csv", source_abs_path)
