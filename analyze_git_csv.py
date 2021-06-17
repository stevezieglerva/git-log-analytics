import glob
import json
import math
import mimetypes
import os
import sys
from collections import namedtuple
from datetime import datetime, timedelta

import pandas as pd
import matplotlib.pyplot as plt

from DateHistogram import DateHistogram
from Histogram import Histogram
from StackedHistogram import StackedHistogram
from StackedDateHistogram import StackedDateHistogram
from TopX import TopX

FileInfo = namedtuple("FileInfo", "file commits complexity age score")


def read_git_log_csv(filename):
    df = pd.read_csv(filename)
    df["file_abbr"] = df["file"].map(lambda a: abbreviate_filename(a))
    without_github_user = df[df["author"] != "GitHub"]
    nans_removed = without_github_user.fillna("", inplace=True)
    return without_github_user


def abbreviate_filename(filename):
    folders = filename.split("/")
    number_of_folders = len(folders)
    if number_of_folders >= 4:
        last_folder = number_of_folders - 1
        second_last_folder = last_folder - 1
        return f"{folders[0]}/.../{folders[second_last_folder]}/{folders[last_folder]}"
    return filename


def calculate_file_complexity(source_path):
    glob_path = source_path + "/**/*.*"
    print("\n📄 Source files:")
    print(f"\tReading: {glob_path}")
    results = {}

    non_code_file_count = 0
    for file in glob.glob(glob_path, recursive=True):
        if is_code_file(file):
            file_size = os.path.getsize(file)
            relative_file = file.replace(source_path + "/", "")
            results[relative_file] = file_size
        else:
            non_code_file_count = non_code_file_count + 1
    print(f"\tSkipped non-code files: {non_code_file_count}")
    return results


def calculate_file_commits(df):
    results = {}
    file_commits = df.groupby("file")["commit_hash"].count()
    for file in file_commits.index:
        commits = file_commits.loc[file]
        results[file] = commits
    return results


def get_commit_age(df, now):
    results = {}
    commit_ages = df.groupby("file")["timestamp"].max()
    for file in commit_ages.index:
        max_date_str = commit_ages.loc[file]
        max_date = datetime.strptime(max_date_str, "%Y-%m-%dT%H:%M:%S")
        age = (now - max_date).days
        results[file] = age
    return results


def determine_hotspot_data(
    file_commits, file_complexities, commit_ages, score_func=None
):
    SIX_MONTHS = 180
    if score_func == None:
        score_func = (
            lambda cm, cp, a: cm * cp if a < SIX_MONTHS else math.log(cm * cp, a)
        )

    results = []
    max_score = 0
    for file, commits in file_commits.items():
        commit_age = commit_ages.get(file, 1) + 1
        file_complexity = file_complexities.get(file, 0)
        if file_complexity == 0:
            # print(f"can't find '{file}'")
            pass
        else:
            # print(f"found '{file}': {file_complexity}")
            if commits > 2:
                score = score_func(commits, file_complexity, commit_age)
                if score > max_score:
                    max_score = score
                new_file = FileInfo(
                    file=file,
                    commits=commits,
                    complexity=file_complexity,
                    score=score,
                    age=commit_age,
                )
                results.append(new_file)
    normalized_results = []
    for count, file in enumerate(results):
        new_score = round((file.score / max_score) * 100, 1)
        normalized_score = FileInfo(
            file=file.file,
            commits=file.commits,
            complexity=file.complexity,
            score=new_score,
            age=file.age,
        )
        normalized_results.append(normalized_score)
    return normalized_results


def get_top_hotspots(hotspots, topn=10):
    top_list = TopX(topn)
    for hotspot in hotspots:
        file = hotspot.file
        score = hotspot.score
        top_list.add((score, hotspot))
    hotspot_array = [i[1] for i in top_list.values]
    return hotspot_array


def format_hotspot_for_print(hotspots):
    top_hotspots = get_top_hotspots(hotspots, 10)
    text = "\n🔥 Hotspots \nCommits  Comp.   Age    Score  File\n"
    for hotspot in top_hotspots:
        text = (
            text
            + f"{hotspot.commits:>5} {hotspot.complexity:>8} {hotspot.age:>5} {hotspot.score:>8}  {hotspot.file:}\n"
        )
    text = text + "\n"
    return text


def write_csv_result(file_info):
    with open("output/git_analysis_result.csv", "w") as results_file:
        results_file.write("commits,complexity,file,score\n")
        for file in file_info:
            results_file.write(
                f'{file.commits},{file.complexity},"{file.file}",{file.score}\n'
            )


def is_code_file(path):
    exclude_extensions = [
        ".md",
        ".lock",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".yaml",
        ".yml",
        ".json",
        ".xml",
        ".scss",
    ]
    filename, file_extension = os.path.splitext(path)
    if file_extension in exclude_extensions:
        return False
    return True


def create_charts(df, hotspots):
    df["two_dirs"] = df["dir_1"] + "/" + df["dir_2"]
    df["datetime"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["month"] = df["datetime"].dt.to_period("M")

    create_single_histogram("author", "commit_hash", "unique_count", df)
    create_single_histogram("author", "churn_count", "sum", df)
    create_single_histogram("two_dirs", "commit_hash", "unique_count", df)
    create_single_histogram("file_abbr", "commit_hash", "unique_count", df)
    create_single_stackeddatehistogram("month", "author", df)
    create_single_stackeddatehistogram("month", "two_dirs", df)
    create_single_datehistogram("month", "author", "unique_count", df)
    create_single_datehistogram("month", "commit_hash", "unique_count", df)

    last_month = datetime.now() - timedelta(days=30)
    last_30_days = df[df["datetime"] >= last_month]
    try:
        create_single_stackeddatehistogram(
            "datetime", "author", last_30_days, "_30_days"
        )
        create_single_stackeddatehistogram(
            "datetime", "two_dirs", last_30_days, "_30_days"
        )
    except TypeError as e:
        if str(e) != "no numeric data to plot":
            raise e
    create_bus_factor_chart(df, hotspots)


def create_single_histogram(field, value_field, aggregation, df, filename_suffix=""):
    histogram = Histogram(field, value_field, df)
    histogram.set_chart_type("barh")
    histogram.set_aggregation(aggregation)
    histogram.set_max_groupings(10)
    histogram.save_plot(
        f"output/git_histogram_{field}_{value_field}_{aggregation}{filename_suffix}.png"
    )


def create_single_datehistogram(
    date_field, value_field, aggregation, df, filename_suffix=""
):
    histogram = DateHistogram(date_field, value_field, df)
    histogram.set_chart_type("bar")
    histogram.set_aggregation(aggregation)
    histogram.save_plot(
        f"output/git_datehistogram_{value_field}_{aggregation}{filename_suffix}.png"
    )


def create_single_stackeddatehistogram(
    date_grouping_field, grouping_field, df, filename_suffix=""
):
    histogram = StackedDateHistogram(
        date_grouping_field, grouping_field, "commit_hash", df
    )
    histogram.set_chart_type("area")
    histogram.set_aggregation("unique_count")
    histogram.set_max_groupings(5)
    histogram.save_plot(
        f"output/git_datehistogram_{grouping_field}{filename_suffix}.png"
    )


def create_bus_factor_chart(df, hotspots):
    top_hotspots = get_top_hotspots(hotspots)
    hotspot_files = [f.file for f in top_hotspots]
    hotspot_commit_df = df[df["file"].isin(hotspot_files)]
    without_github_user = hotspot_commit_df[hotspot_commit_df["author"] != "GitHub"]
    recent_date = datetime.now() - timedelta(days=365)
    recent_data = without_github_user[without_github_user["datetime"] >= recent_date]

    hotspot_unique_author_counts = Histogram("file_abbr", "author", recent_data)
    hotspot_unique_author_counts.set_aggregation("unique_count")
    hotspot_unique_author_counts.set_chart_type("barh")
    hotspot_unique_author_counts.set_max_groupings(10)
    hotspot_unique_author_counts.save_plot("output/git_histogram_bus_factor.png")

    bus_factor_text = ""
    for file in recent_data["file_abbr"].unique():
        unique_authors = recent_data[recent_data["file_abbr"] == file][
            "author"
        ].unique()
        if len(unique_authors) == 1:
            bus_factor_text = bus_factor_text + f"{file:<50} - {unique_authors[0]}\n"
    if bus_factor_text != "":
        print("\n🚌 Hotspots with a high bus factor:")
        print(bus_factor_text)


def create_html_file(csv_file, print_text):
    html = f"""<html>
    <head>
        <title>Git Analysis - {csv_file}</title>
        <style>
            h1 {{color: darkblue}}
            h2 {{color: #507786}}
            h3 {{color: #539DC2}}
        </style>
    </head>
    <body>
        <h1>Git Analysis for: {csv_file}</h1>

        <h2>Total Commits</h2>
        Shows total commits over time <br/>
        <br/>
            <img src="git_datehistogram_commit_hash_unique_count.png"></img><br/>
        <hr/>

        <h2>Unique Authors</h2>
        Shows the number of unique authors making commits per month <br/>
        <br/>
            <img src="git_datehistogram_author_unique_count.png"></img><br/>
        <hr/>


        <h2>Commits By Top Directories</h2>
        Shows commits by the first two directories of the project to visualize what was worked on over time <br/>
        <br/>
            <h3>All Time:</h3>
            <img src="git_datehistogram_two_dirs.png"></img><br/>
            <h3>Last 30 Days:</h3>
            <img src="git_datehistogram_two_dirs_30_days.png"></img><br/>
        <hr/>

        <h2>Commits By Top Author</h2>
        Shows commits by the tops author to visualize who was working and when <br/>
        <br/>
            <h3>All Time:</h3>
            <img src="git_datehistogram_author.png"></img><br/>
            <h3>Last 30 Days:</h3>
            <img src="git_datehistogram_author_30_days.png"></img><br/>
        <hr/>

        <h2>Top Commits</h2>
            <h3>By Author:</h3>
            Shows commits by author to show the top contributors <br/>
            <br/>
            <img src="git_histogram_author_commit_hash_unique_count.png"></img><br/>

            <h3>By File:</h3>
            Shows commits by file to show the busiest file <br/>
            <br/>
            <img src="git_histogram_file_abbr_commit_hash_unique_count.png"></img><br/>

            <h3>By Directory:</h3>
            Shows commits by parent directory to show the busiest parent directory <br/>
            <br/>            
            <img src="git_histogram_two_dirs_commit_hash_unique_count.png"></img><br/>
        <hr/>

        <h2>Hotspots</h2>
            Shows hotspot files in the code that are: <br/>
            <ul>
                <li>complex as measured by file size</li>
                <li>changing frequently as measured by the number of commits</li>
                <li>recent having changed within 365 days</li>
            </ul>

            <pre>
            {print_text}
            </pre>
            <h3>Possible High Bus Factor:</h3>
            Show the number of unique authors per hotspot file in the last year. If a hotspot file only has one author for the last 365 day, it has a high "bus factor" if that person left the team.<br/>
            <img src="git_histogram_bus_factor.png"></img><br/>

    </body>
</html>
"""
    with open("output/results.html", "w") as file:
        file.write(html)


def do_analysis(csv_file, source_path):
    df = read_git_log_csv(csv_file)
    file_commits = calculate_file_commits(df)
    commit_ages = get_commit_age(df, datetime.now())
    print("\n📅 Commit history")
    print(f"\tRead file commits: {len(file_commits)}")

    file_complexities = calculate_file_complexity(source_path)
    print(f"\tRead file complexities: {len(file_complexities)}")

    hotspot_data = determine_hotspot_data(file_commits, file_complexities, commit_ages)
    write_csv_result(hotspot_data)
    print_text = format_hotspot_for_print(hotspot_data)
    print(print_text)

    print("📈 Creating graphs")
    create_charts(df, hotspot_data)

    create_html_file(source_path, print_text)
    print("\n✅  Done!\n\n")


if __name__ == "__main__":
    do_analysis(sys.argv[1], sys.argv[2])
