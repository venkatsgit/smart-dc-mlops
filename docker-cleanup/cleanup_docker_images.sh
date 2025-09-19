#!/bin/bash

# Loop through all unique repositories
docker images --format "{{.Repository}}" | sort -u | while read repo; do
    # Get all images for this repo, sorted by creation time (newest first)
    images=($(docker images --format "{{.ID}} {{.CreatedAt}}" $repo | sort -rk2 | awk '{print $1}'))

    # Keep the first image (newest), delete the rest
    for old_image in "${images[@]:1}"; do
        echo "Removing old image $old_image from $repo"
        docker rmi -f $old_image
    done
done