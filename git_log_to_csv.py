import argparse
import re
import sys
from datetime import datetime


def create_csv(filename, exclude_file_pattern, exclude_author_pattern):
    print(f"exclude_author_pattern:{exclude_author_pattern}")
    print(f"🗓️  Reading git log: {filename}")
    git_log_text = ""
    with open(filename, "r") as file:
        git_log_text = file.read()

    csv_data = process_git_log(
        git_log_text, exclude_file_pattern, exclude_author_pattern
    )

    with open("output/git_log.csv", "w") as file:
        file.write(csv_data)


def strip_timezone_offset(timestamp_str):
    timezone_offset_pattern = "[+\-][0-9][0-9]:[0-9][0-9]$"
    return re.sub(timezone_offset_pattern, "", timestamp_str)


def get_churn_int_values_even_if_dash(text_number):
    metric = 1
    if text_number.strip() != "-":
        metric = int(text_number)
    return metric


def get_first_directories_from_filename(file):
    file_dir_parts = file.split("/")
    results = []
    dir_1 = ""
    dir_2 = ""
    dir_3 = ""
    dir_4 = ""
    if len(file_dir_parts) >= 2:
        dir_1 = file_dir_parts[0]
    if len(file_dir_parts) >= 3:
        dir_2 = file_dir_parts[1]
    if len(file_dir_parts) >= 4:
        dir_3 = file_dir_parts[2]
    if len(file_dir_parts) >= 5:
        dir_4 = file_dir_parts[3]
    return [dir_1, dir_2, dir_3, dir_4]


def process_git_log(log, exclude_file_pattern="", exclude_author_pattern=""):
    commits = log.split("^^")

    result = "commit_hash,epoch,timestamp,date,year,month,day,author,file,churn_count,dir_1,dir_2,dir_3,dir_4\n"
    for number, commit in enumerate(commits):
        if commit != "":
            commit_lines = commit.split("\n")
            commit_basics = commit_lines[0]
            commit_basics_parts = commit_basics.split("--")
            hash = commit_basics_parts[0]
            epoch = commit_basics_parts[1]
            tmsp = commit_basics_parts[2]

            # 2019-12-17T09:16:10-05:00
            # yyyy-mm-ddT
            tmsp = strip_timezone_offset(tmsp)
            tmsp_date = datetime.strptime(tmsp, "%Y-%m-%dT%H:%M:%S")
            day_only = tmsp_date.date()
            year = tmsp_date.year
            month = tmsp_date.month
            day = tmsp_date.day

            author = commit_basics_parts[3]
            if include_author(author, exclude_author_pattern):
                total_lines = len(commit_lines)
                for row_index in range(3, total_lines - 1):
                    churn_line = commit_lines[row_index]
                    churn_line_parts = churn_line.split("\t")
                    insertions = get_churn_int_values_even_if_dash(churn_line_parts[0])
                    deletions = get_churn_int_values_even_if_dash(churn_line_parts[1])
                    total_churn = insertions + deletions

                    file = churn_line_parts[2]
                    if include_file(file, exclude_file_pattern):
                        dirs = get_first_directories_from_filename(file)

                        result = (
                            result
                            + f'{hash},{epoch},{tmsp},{day_only},{year},{month},{day},"{author}","{file}",{total_churn},{dirs[0]},{dirs[1]},{dirs[2]},{dirs[3]}\n'
                        )

    return result


def include_file(file, exclude_file_pattern):
    if exclude_file_pattern != "" and re.findall(
        exclude_file_pattern, file, re.IGNORECASE
    ):
        return False
    return True


def include_author(author, exclude_author_pattern):
    if exclude_author_pattern != "" and re.findall(
        exclude_author_pattern, author, re.IGNORECASE
    ):
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename",
        type=str,
        help="filename of the csv logfile",
    )
    parser.add_argument(
        "filename",
        type=str,
        help="filename of the csv logfile",
    )
    args = parser.parse_args()
    print(args.accumulate(args.integers))
    create_csv(args.file)
