#!/bin/bash

repos=("../mobile-market-info-v1/" "../golia-market-info-v1/" "../ndce-market-info-v1/" )
help_option=false

while getopts "r:hl" flags; do
    case "$flags" in
        h)
            help_option=true
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
    echo "This script is intended to be used to push development branches of different repo to origin all at once." 
    echo "This script will perform the same operations for all three be4fe (or just the lib repo if -l is passed)!"
    echo "Options:"
    echo "  -l    to operate the updates only into lib-market-info's repo"
    echo "  -h    Display this help message"
    echo "  -r    path repo list (E.G. ../my-repo)"
    exit 0
fi

for repo in "${repos[@]}"; do

    echo "Pushing $repo's current branch"

    git -C "$repo" pull
    git -C "$repo" push 

    echo

done
