#!/bin/bash

repos=("../mobile-market-info-v1/" "../golia-market-info-v1/" "../ndce-market-info-v1/" "../lib-market-info-v1/")

if [ $# -gt 0 ]; then
    repos=("$@")
fi

for repo in "${repos[@]}"; do

    echo "Pruning $repo's branches..."

    git -C "$repo" checkout "env/svil"
    git -C "$repo" branch | grep -v "env/svil" | xargs git -C "$repo" branch -D
    
    echo
done
