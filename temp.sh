

git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch sample/git_log.csv" \
  --prune-empty --tag-name-filter cat -- --all
