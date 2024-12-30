#!/usr/bin/env bash

#!/usr/bin/env bash
# check if gh cli is installed
cmd="gh"
[[ $(type -P "$cmd") ]] && echo "$cmd is in PATH"  ||
    { echo "$cmd is NOT in PATH. Install gh cli first" 1>&2; exit 1; }

# check if gh milestone is properly installed
# ref: https://github.com/valeriobelli/gh-milestone
[[ $(gh milestone 2>/dev/null) ]] ||
    { echo "Install gh milestone from https://github.com/valeriobelli/gh-milestone first!"; exit 1; }

# get the name of the repo
reponame=$(gh repo view --json name -q ".name")

# date command is gdate on mac
os=$(uname -a|awk '{print $1}')
if [ "$os" == "Darwin" ];then
	date="gdate"
elif [ "$os" == "Linux" ];then
	date="date"
else
	date="date"
fi

# get current year
y=$($date +"%Y")

# Days of the week
# 1 = Mon
# 2 = Tue
# ...
# 6 = Sat
# 7 = Sun
# find first Sat of the year
for d in {0..6}
do
    if (( $($date -d "$y-1-1 + $d day" '+%u') == 6))   #
    then
        break
    fi
done

# get current week
cweek=$($date +'%W')
week=0
for ((w = d; w <= $($date -d "$y-12-31" '+%j') - 1; w += 7))
do
    week=$((week+1))
    if [ "$week" -lt "$cweek" ];then
        continue
    fi
    dd=$($date -d "$y-1-1 + $w day" '+%Y-%m-%d')
    m=$(echo $dd|awk -F"-" '{print $2}')
    d=$(echo $dd|awk -F"-" '{print $3-1}')
    d=$(printf "%02d\n" $d)
    week1=$(printf "%02d\n" $week)
    title="${y}w${week1}_${m}${d}"
    echo gh milestone create --title $title --due-date $dd
    gh milestone create --title $title --due-date $dd
done
