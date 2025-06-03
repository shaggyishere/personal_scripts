#!/bin/bash
help_option=false
is_defined_repos=false
only_lib=false
profile=""
SCRIPT_DIR=$(dirname "$0")

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
    echo "Usage: $0 [-R] [-h] [-p project] [-b branch_name]"
    echo "This script is intended to be used to push development branches of different repo to origin all at once." 
    echo "This script will perform the same operations for all three be4fe (or just the lib repo if -l is passed)!"
    echo "Options:"
    echo "  -l    to operate only into lib repos"
    echo "  -p    to set the .env file to load"
    echo "  -h    Display this help message"
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

    echo "Pushing $repo's current branch"

    git -C "$repo" pull
    git -C "$repo" push 

    echo

done
