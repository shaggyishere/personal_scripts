#!/bin/bash

help_option=false
repos=("../mobile-market-info-v1/" "../golia-market-info-v1/" "../ndce-market-info-v1/" "../lib-market-info-v1/")

while getopts "r:h" flags; do
    case "$flags" in
        h)
            help_option=true
            ;;
        r)
            IFS=',' read -r -a repos <<< "$OPTARG"
            ;;
    esac
done

if [ "$help_option" = true ]; then
    echo "Usage: $0 [-h] [-r path_to_repo1,path_to_repo2]"
    echo "This script is intended to be used just to show current branches." 
    echo "This script will perform the same operations for all three be4fe and lib repos if repo is not specified with -r flag!"
    echo "Options:"
    echo "  -h    Display this help message"
    echo "  -r    path repo list (E.G. ../my-repo)"
    exit 0
fi

for repo in "${repos[@]}"; do

    echo "Showing $repo's current branch"

    git -C "$repo" branch
    
    echo
done
