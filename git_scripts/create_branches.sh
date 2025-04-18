#!/bin/bash

help_option=false
only_lib=false
branch=""
profile=""
SCRIPT_DIR=$(dirname "$0")


while getopts "p:b:r:hl" flags; do
    case "$flags" in
        h)
            help_option=true
            ;;
        p)
            profile=$OPTARG
            ;;
        b)
            branch=$OPTARG
            ;;
        r)
            IFS=',' read -r -a repos <<< "$OPTARG"
            ;;
        l)
            only_lib=true
            ;;
    esac
done

if [[ -z "$profile" ]]; then
  echo "Error: -p <project> is required"
  exit 1
fi

if [[ -z "$branch" ]]; then
  echo "Error: -b <branch> is required"
  exit 1
fi

if [ "$help_option" = true ]; then
    echo "Usage: $0 [-h] [-b branch_name] [-p project] [-r path_to_repo1,path_to_repo2]"
    echo "This script is intended to be used when it's necessary to create a new branch." 
    echo "This script will perform the same operations for all three be4fe (or just the lib repo if -l is passed)!"
    echo "Options:"
    echo "  -h    Display this help message"
    echo "  -b    to set the branch name to create"
    echo "  -p    to set the .env file to load"
    echo "  -r    path repo list (E.G. ../my-repo)"
    exit 0
fi

env_file=".env.${profile}"

if [[ -f "$SCRIPT_DIR/.env.$profile" ]]; then
  source "$SCRIPT_DIR/.env.$profile"
else
  echo "Error: Environment file '$env_file' not found!"
  exit 1
fi

if [ "$only_lib" = true ]; then
  repos=("${lib_repos[@]}")
fi

for repo in "${repos[@]}"; do

    echo "Updating $repo"

    git -C "$repo" checkout "env/svil"
    git -C "$repo" pull
    git -C "$repo" checkout -b "$branch"
    git -C "$repo" push --set-upstream origin "$branch"
    
    echo
done
