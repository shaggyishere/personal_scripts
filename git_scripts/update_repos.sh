#!/bin/bash

release_option=false
help_option=false
is_defined_repos=false
branch=""
only_lib=false
profile=""
SCRIPT_DIR=$(dirname "$0")

while getopts "p:b:r:Rhl" flags; do
    case "$flags" in
        R)
            release_option=true
            ;;
        p)
            profile=$OPTARG
            ;;
        h)
            help_option=true
            ;;
        b)
            branch=$OPTARG
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

if [ "$help_option" = true ]; then
    echo "Usage: $0 [-R] [-h] [-p project] [-b branch_name]"
    echo "This script is intended to be used when a CR lifecycle is being closed (merged from PR) and the $default_development_branch branch is to be updated to the origin" 
    echo "This script will perform the same operations for all three be4fe (or just the lib repo if -l is passed)!"
    echo "Options:"
    echo "  -l    to operate the updates only into lib repos"
    echo "  -R    add a RELEASE comment on top and push it to origin"
    echo "  -h    Display this help message"
    echo "  -p    to set the .env file to load"
    echo "  -b    to set a specific branch to checkout into"
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

# default branch to checkout to, $default_development_branch should be valued in .env file
branch=$default_development_branch

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
