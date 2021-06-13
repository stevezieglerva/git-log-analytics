export repo_dir_name=$1

# cd ../$repo_dir_name
# echo "Get the latest code for $repo_dir_name"
# git pull

# echo "Create the log csv"
# git log --reverse --all -M -C --numstat --format="^^%h--%ct--%cI--%an%n" > git_log.txt
# cd ../git-log-analytics/

echo "Analyze the log"
python3 main.py ../$repo_dir_name/git_log.txt

open output/results.html


