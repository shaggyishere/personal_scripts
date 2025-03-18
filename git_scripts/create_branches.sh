#!/bin/bash

help_option=false
branch=""

repos=("../mobile-market-info-v1/" "../golia-market-info-v1/" "../ndce-market-info-v1/" )

while getopts "b:r:hl" flags; do
    case "$flags" in
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

if [[ -z "$branch" ]]; then
  echo "Error: -b <branch> is required"
  exit 1
fi

if [ "$help_option" = true ]; then
    echo "Usage: $0 [-h] [-b branch_name] [-r path_to_repo1,path_to_repo2]"
    echo "This script is intended to be used when it's necessary to create a new branch." 
    echo "This script will perform the same operations for all three be4fe (or just the lib repo if -l is passed)!"
    echo "Options:"
    echo "  -h    Display this help message"
    echo "  -b    to set the branch name to create"
    echo "  -r    path repo list (E.G. ../my-repo)"
    exit 0
fi

for repo in "${repos[@]}"; do

    echo "Updating $repo"

    git -C "$repo" checkout "env/svil"
    git -C "$repo" pull
    git -C "$repo" checkout -b "$branch"
    git -C "$repo" push --set-upstream origin "$branch"
    
    echo
done
