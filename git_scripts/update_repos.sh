#!/bin/bash

repos=("../mobile-market-info-v1/" "../golia-market-info-v1/" "../ndce-market-info-v1/" )
release_option=false
help_option=false
branch="env/svil"

while getopts "b:Rhl" flags; do
    case "$flags" in
        R)
            release_option=true
            ;;
        h)
            help_option=true
            ;;
        b)
            branch=$OPTARG
            ;;
        r)
            IFS=',' read -r -a repos <<< "$OPTARG"
            ;;
        l)
            repos=("../lib-market-info-v1/")
            ;;
    esac
done

if [ "$help_option" = true ]; then
    echo "Usage: $0 [-R] [-h] [-b branch_name]"
    echo "This script is intended to be used when a CR lifecycle is being closed (merged from PR) and the env/svil branch is to be updated to the origin" 
    echo "This script will perform the same operations for all three be4fe (or just the lib repo if -l is passed)!"
    echo "Options:"
    echo "  -l    to operate the updates only into lib-market-info's repo"
    echo "  -R    add a RELEASE comment on top and push it to origin"
    echo "  -h    Display this help message"
    echo "  -b    to set a specific branch to checkout into"
    echo "  -r    path repo list (E.G. ../my-repo)"
    exit 0
fi

for repo in "${repos[@]}"; do

    echo "Updating $repo"

    git -C "$repo" fetch
    git -C "$repo" checkout "$branch"
    git -C "$repo" pull
    if [ "$release_option" = true ]; then
        git -C "$repo" commit --allow-empty -m "RELEASE"
        git -C "$repo" push 
    fi

    echo

done
