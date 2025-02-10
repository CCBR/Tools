#!/usr/bin/env bash
#valeriobelli/gh-milestone
#GitHub CLI extension for managing Milestones

workflow=$1
year="$2"
run=$3


if [[ -z $workflow ]]; then echo "Choose a workflow: HELP, INSTALL, WEEKLY, MONTHLY, CONVERSION, EDIT, DELETE"; exit; fi
if [[ -z $year ]] && [[ $workflow != "HELP" ]]; then echo "You must provide a year!"; exit; fi
if [[ -z $run ]] && [[ $workflow != "HELP" ]]; then run="OFF"; fi

# on mac change "date" to "gdate" on the next command
# if you dont have "gdate" on mac .. install using:
# brew install coreutils
if [ "$os" == "Darwin" ];then
    date="gdate"
elif [ "$os" == "Linux" ];then
    date="date"
else
    date="date"
fi

####################################################
# Install software
####################################################
if [[ $workflow == "INSTALL" ]]; then
    echo "--INSTALLING"
    brew install gh
    gh extension install valeriobelli/gh-milestone
####################################################
# Create weekly milestones
####################################################
elif [[ $workflow == "WEEKLY" ]]; then
    echo "--WEEKLY"
    # run through days
    for d in {0..6}; do
        if (( $($date -d "$y-1-1 + $d day" '+%u') == 6))
        # +%w: Sat == 6 also
        then
            break
        fi
    done

    # run through week
    week=0
    for ((w = d; w <= $($date -d "$y-12-31" '+%j') - 1; w += 7)); do
        week=$((week+1))
        if [ "$week" -le "1" ];then
            continue
        fi
        dd=$($date -d "$y-1-1 + $w day" '+%Y-%m-%d')
        m=$(echo $dd|awk -F"-" '{print $2}')
        d=$(echo $dd|awk -F"-" '{print $3-1}')
        d=$(printf "%02d\n" $d)
        week1=$(printf "%02d\n" $week)
        title="${y}w${week1}_${m}${d}"
        echo "gh milestone create --title $title --due-date $dd"
        gh milestone create --title $title --due-date $dd
    done
####################################################
# Create monthtly milestones
####################################################
elif [[ $workflow == "MONTHLY" ]]; then
    echo "--MONTHLY"
    #!/bin/bash
    for i in {1..12}; do
        mon=$(echo $i|awk '{printf("%02d",$1)}')
        lastday=$(eval cal "$mon $year"|awk 'NF {DAYS = $NF}; END {print DAYS}')
        duedate="${year}-${mon}-${lastday}"
        title="${year}-${mon}"

        ### RUN
        if [[ $run == "RUN" ]]; then
            echo "------- RUNNING -------"
            gh milestone create --title $title --due-date $duedate
        else
            echo "------- COMMANDS TO RUN-------"
            echo "gh milestone create --title $title --due-date $duedate"
        fi
    done
####################################################
# Convert weekly to monthly
####################################################
elif [[ $workflow == "CONVERSION" ]]; then
    echo "--CONVERSION"
    # remove old copies
    if [[ -f milestone_list.txt ]]; then rm milestone_list.txt; fi
    if [[ -f conversion_table.txt ]]; then rm conversion_table.txt; fi

    # grab all milestones
    gh milestone list --state all | grep github | sed 's/#//g' | awk -v OFS="\t" '{print $1,$2}' | grep $year | grep -v "Cancelled"> milestone_list.txt

    # for each incorrect milestone, generate new one
    while read ghID olddate; do
        month=`echo $olddate | awk -F"_" '{ print $2 }' | awk '{print substr($0,1,2)}'`
        echo -e "$ghID\t$olddate\t$year"-"$month" >> conversion_table.txt
    done < milestone_list.txt
    cat conversion_table.txt

####################################################
# Edit Issues
####################################################
elif [[ $workflow == "EDIT" ]]; then
    while read msn oms nms; do
        for i in $(gh issue list --milestone "$oms" --state all | awk '{print $1}'); do

            ### RUN
            if [[ $run == "RUN" ]]; then
                echo "------- RUNNING -------"
                gh issue edit $i --milestone "$nms";
            else
                echo "------- COMMANDS TO RUN-------"
                echo "gh issue edit $i --milestone "$nms""
            fi
        done
    done < conversion_table.txt
####################################################
# Delete Issues
####################################################
elif [[ $workflow == "DELETE" ]]; then
    while read msn oms nms; do
            ### RUN
            if [[ $run == "RUN" ]]; then
                echo "------- RUNNING -------"
                gh milestone delete $msn --confirm
            else
                echo "------- COMMANDS TO RUN-------"
                echo "gh milestone delete $msn --confirm"
            fi
    done < conversion_table.txt
####################################################
# Error check
####################################################
# Error check
####################################################
else
    echo
    echo "************************************************"
    echo "**************** COMMANDS *********************"
    echo "Choose a workflow:"
    echo "INSTALL, WEEKLY, MONTHLY, CONVERSION, EDIT"
    echo
    echo "Choose a year:"
    echo "2023 2024"
    echo
    echo "Choose a fate:"
    echo "ECHO RUN"
    echo
    echo "************************************************"
    echo "**************** EXAMPLES *********************"
    echo "Test monthly milestones: bash github_milestones.sh MONTHLY 2023 ECHO"
    echo "Create monthly milestones: bash github_milestones.sh MONTHLY 2023 RUN"
    echo
    echo "Create conversion table for milestones: bash github_milestones.sh CONVERSION 2023"
    echo
    echo "Test conversion of milestones: bash github_milestones.sh EDIT 2023 ECHO"
    echo "Perform conversion of milestones: bash github_milestones.sh EDIT 2023 RUN"
fi
