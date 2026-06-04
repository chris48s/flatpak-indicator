#!/bin/bash

set -euo pipefail

# read version + ensure non-empty
VERSION="$1"
[ -z "$VERSION" ] &&  echo "Error: No version specified" && exit 1

# ensure work tree is clean (aside from debian/changelog)
if [[ ! $(git status --porcelain | grep -vc "debian/changelog") -eq 0 ]]; then
    echo "Error: Uncommitted changes in work tree"
    exit 1
fi

# ensure we're on default branch
if [[ ! "$(git branch --show-current)" =~ ^(main|master)$ ]]; then
    echo "Error: Not on default branch"
    exit 1
fi

# ensure the changelog is up-to-date
if ! (grep -q "$VERSION" debian/changelog)
then
    echo "Error: debian/changelog is not up to date"
    exit 1
fi

# confirm
read -r -p "Bump version from $(poetry version --short) to $VERSION. Are you sure? [y/n] " response
response=${response,,}  # tolower
if [[ ! "$response" =~ ^(yes|y)$ ]]; then
    exit 1
fi

# checks done, now publish the release...

# bump version
poetry version "$VERSION"

# commit
git add pyproject.toml
git add debian/changelog
git commit -m "version $VERSION"

# tag
git tag "$VERSION"

# push to GitHub
git push origin "$(git branch --show-current)" --tags
