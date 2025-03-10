#!/bin/bash

release_option=false

# -r argument is used to RELEASE
while getopts "r" flags; do
    case "$flags" in
        r)
            release_option=true
            ;;
    esac
done

echo "Updating lib-market-info-v1/..."

git -C "lib-market-info-v1/" checkout env/svil
git -C "lib-market-info-v1/" pull
if [ "$release_option" = true ]; then
    git -C "lib-market-info-v1/" commit --allow-empty -m "RELEASE"
    git -C "lib-market-info-v1/" push 
fi
