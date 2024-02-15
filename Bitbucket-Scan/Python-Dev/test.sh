#!/bin/sh

# git ls-remote -h ssh://git@stash.hotelbeds:7999/train/gsantandreu-training.git 

set -e -u



git ls-remote ssh://git@stash.hotelbeds:7999/train/gsantandreu-training.git 'refs/heads/*' | while read sha ref; do
  # test if $sha is merged
  E='git cat-file -t "$sha" 2>&1'
  test $? -ne 0 -a "${E#*git cat-file: *}" = "could not get object info" && continue
  git branch --merged "$sha" && printf ':%s\0' "$ref"
done
