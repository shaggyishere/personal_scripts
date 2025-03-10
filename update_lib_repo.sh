#!/bin/bash

release_option=false
branch="env/svil"


while getopts "b:r" flags; do
    case "$flags" in
        r)
            release_option=true
            ;;
        b)
            branch=$OPTARG
            ;;
    esac
done

echo "Updating lib-market-info-v1/..."

git -C "lib-market-info-v1/" fetch
git -C "lib-market-info-v1/" checkout "$branch"
git -C "lib-market-info-v1/" pull
if [ "$release_option" = true ]; then
    git -C "lib-market-info-v1/" commit --allow-empty -m "RELEASE"
    git -C "lib-market-info-v1/" push 
fi
