#!/bin/bash

help_option=false
is_defined_repos=false
profile=""
SCRIPT_DIR=$(dirname "$0")
only_lib=false

while getopts "p:r:hl" flags; do
    case "$flags" in
        h)
            help_option=true
            ;;
        p)
            profile=$OPTARG
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
    echo "Usage: $0 [-h] [-p project] [-r path_to_repo1,path_to_repo2]"
    echo "This script is intended to be used when it's necessary to delete all local dev branch except env/svil one." 
    echo "This script will perform the same operations for all three be4fe and lib repos if repo is not specified with -r flag!"
    echo "Options:"
    echo "  -h    Display this help message"
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

if [ "$is_defined_repos" = true ]; then
  repos=("${defined_repos[@]}")
fi

for repo in "${repos[@]}"; do

    echo "Pruning $repo's branches"

    git -C "$repo" checkout "env/svil"
    git -C "$repo" branch | grep -v "env/svil" | xargs git -C "$repo" branch -D
    
    echo
done
