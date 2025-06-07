#!/bin/bash

REPO_API="https://api.github.com/repos/mediaselect/select-freeboxos-docker/commits/master"
LOCAL_COMMIT_FILE="$HOME/.config/.last_commit"

latest_commit=$(curl -s $REPO_API | jq -r '.sha')

if [ -z "$latest_commit" ]; then
    echo "Failed to fetch the latest commit hash from GitHub." >&2
    exit 1
fi
# Compare with the last commit
if [ -f "$LOCAL_COMMIT_FILE" ]; then
    last_commit=$(cat "$LOCAL_COMMIT_FILE")
    if [ "$last_commit" == "$latest_commit" ]; then
        exit 0
    fi
fi

wget https://github.com/mediaselect/select-freeboxos-docker/archive/refs/heads/master.zip -O /tmp/select-freeboxos.zip
if [ $? -ne 0 ]; then
    echo "Download failed."
    exit 1
fi

[ -d "$HOME/select-freeboxos" ] && rm -rf "$HOME/select-freeboxos"

unzip -o /tmp/select-freeboxos.zip -d "$HOME"
if [ $? -ne 0 ]; then
    echo "Unzip failed."
    exit 1
fi
rm /tmp/select-freeboxos.zip
mv "$HOME/select-freeboxos-docker-master" "$HOME/select-freeboxos"


echo "$latest_commit" > "$LOCAL_COMMIT_FILE"

echo "Program updated successfully."
