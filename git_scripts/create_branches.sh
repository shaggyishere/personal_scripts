#!/bin/bash

help_option=false
is_defined_repos=false
only_lib=false
branch_to_create=""
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
            branch_to_create=$OPTARG
            ;;
        r)
            is_defined_repos=true
            IFS=',' read -r -a defined_repos <<< "$OPTARG"
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

if [[ -z "$branch_to_create" ]]; then
  echo "Error: -b <branch_to_create> is required"
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
    echo "  -l    to operate only into lib repos"
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

if [ "$is_defined_repos" = true ]; then
  repos=("${defined_repos[@]}")
fi

for repo in "${repos[@]}"; do

    echo "Updating $repo"

    git -C "$repo" checkout "$default_development_branch"
    git -C "$repo" pull
    git -C "$repo" checkout -b "$branch_to_create"
    git -C "$repo" push --set-upstream origin "$branch_to_create"
    
    echo
done
