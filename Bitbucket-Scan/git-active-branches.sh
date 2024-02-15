#!/bin/sh
set -eu

DEFAULT_SINCE='3.weeks.ago'
since=$DEFAULT_SINCE

usage() {
    echo "usage: git active-branches [-s|-a <date>]" >&2
    echo >&2
    echo "Options:" >&2
    echo "-s      show branches active since <date> (as in 'git log --since')" >&2
    echo "-a      (an alias for '-s')" >&2
    echo "<date>  any date format recognized by 'git log'" >&2
    echo >&2
    echo "Unless specified, <date> defaults to \"$DEFAULT_SINCE\". For examples see:" >&2
    echo "https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History" >&2
}

while [ $# -gt 0 ]; do
    if ! getopts a:s:h flag; then usage; exit 2; fi
    case "$flag" in
        a|s) since=$OPTARG; shift ;;
        \?)  usage; exit 2 ;;  # argument missing its option
        h)   usage; exit 2 ;;
    esac
    shift
done

( git local-branches; git remote-branches ) | while read branch; do
    # '--no-patch' = suppress diff output (long form of '-s')
    maybebranch=$(
        git log -1 --since="$since" --no-patch "$branch"
    )
    [ -n "$maybebranch" ] && echo "$branch"
done