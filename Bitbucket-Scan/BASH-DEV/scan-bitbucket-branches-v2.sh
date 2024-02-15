#!/bin/bash


# To DEBUG use: read -p "Test: "
# To calculate the elapsed time
start_time=$(date +%s)

### Testing curl's
#curl -k -H 'Authorization: Basic bHBlbGF5by5pdDpEbDIyI29jdDIyMDA=' -X GET -H "Content-type: application/json" https://bitbucket.hotelbeds.com/rest/api/1.0/projects?limit=2000
#curl -k -H 'Authorization: Basic bHBlbGF5by5pdDpEbDIyI29jdDIyMDA=' -X GET -H "Content-type: application/json" https://bitbucket.hotelbeds.com/rest/api/1.0/projects/ANS/repos?limit=2000
#curl -k -H 'Authorization: Basic bHBlbGF5by5pdDpEbDIyI29jdDIyMDA=' -X GET -H "Content-type: application/json" https://bitbucket.hotelbeds.com/rest/api/1.0/projects/ANS/repos/ansible/branches?base=refs%2Fheads%2Fmaster&details=true&limit=500

### Variables defined
bitbucket_url=https://bitbucket.hotelbeds.com
# If you are allready logged in Bitbucket from the Computer, keep the auth_header commented.... this is for user & pass.
# auth_header='Authorization: Basic bHBlbGF5by5pdDpMbDAzI2FnbzIzMDA='
conten_type="Content-type: application/json"
report=bitbucket_report.csv

# ### Delete the file generated in previous exec.
# file="bitbucket-scan-results.csv"
# if [ -f "$file" ] ; then
#     rm "$file"
# fi


### Delete previus execution log
file="scan-log.txt"
if [ -f "$file" ] ; then
    rm "$file"
fi

### Get the list of all the projects from Bitbucket account across all the pages
get_total_project_list () {

   	total_project_list=()

    response=$(curl -s -k -H "${auth_header}" -X GET -H "${content_type}" $bitbucket_url/rest/api/1.0/projects?limit=2000) 2>&1
	total_project_list=$(echo "${response}" | jq '.values[].key' | sed -e 's/"//g')

}


### Get the list of all repositories from each project listed above across the pages
get_total_repository_list() {
	echo ">>> Project is: $1"
	total_repo_list=()

    response=$(curl -s -k -H "${auth_header}" -X GET -H "${content_type}" $bitbucket_url/rest/api/1.0/projects/$1/repos?limit=2000) 2>&1

    total_repo_list=$(echo "${response}" | jq '.values[].name' | sed -e 's/"//g')
    total_repo_list=${total_repo_list//[ ]/-}

}


### Get the info of the branches .... Commented because we dont needed right now
get_branches_by_repository() {
	project_key=$1
	repository_key=$2

	start=0
	total_branch_list=()
	is_last_page=false

	while ! $is_last_page

	do
		response=$(curl -s -k -H "${auth_header}" -X GET -H "${content_type}" $bitbucket_url/rest/api/1.0/projects/$1/repos/$2'/branches?details=true&limit=100&start='$start) 2>&1
		size=$(echo "${response}" | jq '.size')
        is_last_page=$(echo "${response}" | jq '.isLastPage')

        # echo $response
        # echo $size
        # echo $is_last_page
        
        # use start only in case of no set limit.... because when use high limit & there is only one page ... the key: isLastPage no appear in the response
		start=$(echo "${response}" | jq '.nextPageStart')
        # echo -e "START: $start"

        #read
        #size=$((size-1))
        # echo $size
        for n in $(seq 0 $((size-1)))

        do
            # echo "valor de n = ${n}"
            values_n=$(echo "${response}" | jq ".values[${n}]")
            # echo $values_n

            #Fields
            displayId_n=$(echo "${response}" | jq ".values[${n}].displayId")
            # echo $displayId_n

            # latestCommit_n=$(echo "${response}" | jq ".values[${n}].latestCommit")
            # echo $latestCommit_n

            # ahead_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-branch:ahead-behind-metadata-provider".ahead')
            # echo $ahead_n

            # behind_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-branch:ahead-behind-metadata-provider".behind')
            # # echo $behind_n

            # author_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-branch:latest-commit-metadata".author.emailAddress')
            # # echo $author_n

            # msg_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-branch:latest-commit-metadata".message')
            # # echo $msg_n

            # committerTime_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-branch:latest-commit-metadata".committerTimestamp')
            # # echo $committerTime_n
            # committerTime_n=$(expr $committerTime_n / 1000)
            # committerTime_n=$(date -d@"$committerTime_n" +"%d-%m-%Y")
            # # echo $committerTime_n

            # pullReqTitle_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.title')
            # echo $pullReqTitle_n

            pullReqState_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.state')
            # echo $pullReqState_n

            # pullReqClosed_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.closed')
            # echo $pullReqClosed_n

            # prCreatedDate_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.createdDate')
            # # echo $prCreatedDate_n
            # if  [[ "$prCreatedDate_n" != 'null' ]]
            # then
            #     prCreatedDate_n=$(expr $prCreatedDate_n / 1000)
            #     prCreatedDate_n=$(date -d@"$prCreatedDate_n" +"%d-%m-%Y")
            #     # echo $prCreatedDate_n
            # fi
            
            # prUpdatedDate_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.updatedDate')
            # # echo $prUpdatedDate_n
            # if  [[ "$prUpdatedDate_n" != 'null' ]]
            # then
            #     prUpdatedDate_n=$(expr $prUpdatedDate_n / 1000)
            #     prUpdatedDate_n=$(date -d@"$prUpdatedDate_n" +"%d-%m-%Y")
            #     # echo $prUpdatedDate_n
            # fi

            prClosedDate_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.closedDate')
            # echo $prClosedDate_n
            if  [[ "$prClosedDate_n" != 'null' ]]
            then
                prClosedDate_n=$(expr $prClosedDate_n / 1000)
                prClosedDate_n=$(date -d@"$prClosedDate_n" +"%d-%m-%Y")
                # echo $prClosedDate_n
            fi 

            prToRef_n=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.toRef.displayId')
            # echo $prToRef_n

            # prRevEmail_n1=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.reviewers[0].user.name')
            # echo $prRevEmail_n1

            # prRevName_n1=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.reviewers[0].user.displayName')
            # echo $prRevName_n1

            # prRevApp_n1=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.reviewers[0].approved')
            # echo $prRevApp_n1

            # prRevEmail_n2=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.reviewers[1].user.name')
            # echo $prRevEmail_n2

            # prRevName_n2=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.reviewers[1].user.displayName')
            # echo $prRevName_n2

            # prRevApp_n2=$(echo "${response}" | jq ".values[${n}].metadata."'"com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.reviewers[1].approved')
            # echo $prRevApp_n2

            # echo -e "$1, $2, $displayId_n, $latestCommit_n, $ahead_n, $behind_n, $author_n, $msg_n, $committerTime_n, $pullReqTitle_n, $pullReqState_n, $pullReqClosed_n, $prCreatedDate_n, $prUpdatedDate_n, $prClosedDate_n, $prToRef_n, $prRevEmail_n1, $prRevName_n1, $prRevApp_n1, $prRevEmail_n2, $prRevName_n2, $prRevApp_n2" >> $report
            echo -e "$1, $2, $displayId_n, $pullReqState_n, $prClosedDate_n, $prToRef_n" >> $report

            # read

        done

        # echo $response > test_branchesdetails.txt

	done

}


### We can use this one by one instead get_branches_by_repository
get_branch_details() {
    project_key=$1
	repository_key=$2

    # Add repo to the log
    echo "##### Querying Prj: $1 ---- Repo: $2" >> scan-log.txt

	start=0
	total_branch_details=()
	is_last_page=false

	while ! $is_last_page

	do

		response=$(curl -k -H "${auth_header}" -X GET -H "${content_type}" $bitbucket_url/rest/api/1.0/projects/$1/repos/$2'/branches?&details=true&limit=1&start='$start) 2>&1
		is_last_page=$(echo "${response}" | jq '.isLastPage')

        # echo $response
        # read -p "Pause" 

        # Extract the merge_status = MERGED to get the values
        merge_st=$(echo "${response}" | jq '.values[].metadata."com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.state')

        # Contruct IF with merge_st=MERGED else continue
        if [[ "$merge_st" == "\"MERGED\"" ]]

        then 
            # Extract the values from the CURL response
            branch_name=$(echo "${response}" | jq '.values[].displayId')
            closed_st=$(echo "${response}" | jq '.values[].metadata."com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.closed')
            createdDate=$(echo "${response}" | jq '.values[].metadata."com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.createdDate')
            updatedDate=$(echo "${response}" | jq '.values[].metadata."com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.updatedDate')
            closedDate=$(echo "${response}" | jq '.values[].metadata."com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.closedDate')
            toRef_id=$(echo "${response}" | jq '.values[].metadata."com.atlassian.bitbucket.server.bitbucket-ref-metadata:outgoing-pull-request-metadata".pullRequest.toRef.displayId')

            # Add branch_name to log
            echo "Branch: $branch_name" >> scan-log.txt

            # Format the dates from EPOCH to datetime
            createdDate=$(expr $createdDate / 1000)
            createdDate=$(date -d@"$createdDate" +"%d-%m-%Y")

            updatedDate=$(expr $updatedDate / 1000)
            updatedDate=$(date -d@"$updatedDate" +"%d-%m-%Y")

            closedDate=$(expr $closedDate / 1000)
            closedDate=$(date -d@"$closedDate" +"%d-%m-%Y")

            # Save to csv
            echo -e "$1, $2, $branch_name, $merge_st, $createdDate, $updatedDate, $closedDate, $toRef_id" >> bitbucket-scan-results.csv

        fi

        # use start only in case of no set limit.... because when use high limit & there is only one page ... the key: isLastPage no appear in the response
		start=$(echo "${response}" | tr '\r\n' ' ' | jq '.nextPageStart')
        echo -e "START: $start"

	done

}

# In case we want to run it with user & password
# read -p "Enter your Bitbucket username: " t

# List of projects
get_total_project_list

# Print Screen the prjs list & save it in txt file
echo ">>> total_project_list is: ${total_project_list[@]}"

# Create csv file with headers
# echo "PROJECT, REPOSITORY, BRANCH_NAME, MERGE, CREATED_DATE, UPDATED_DATE, CLOSED_DATE, MERGED_TO" > bitbucket-scan-results.csv
echo "PROJECT, REPOSITORY, BRANCH_NAME, MERGE, CLOSED_DATE, MERGED_TO" > $report


# Iterate over the prj list to get the repositories
for pkey in ${total_project_list[@]}

do

    # Save the actual prj in temp file to locate the error in case of error
    echo $pkey >> scan-log.txt

    # Call the function get_total_repository_list with the prj as argument
	get_total_repository_list $pkey
	echo -e ">>> total_repo_list is: \n${total_repo_list[@]}"

    # Iterate over repos to get the branches
	for rkey in ${total_repo_list[@]}

	do

        # Call the check_branches_by_repository function with prj and repo as args to get the branches info, this generate txt file with the prj, repo, branches
        echo $pkey $rkey
        # TODO: Add Progress Spinner here by alias
		get_branches_by_repository $pkey $rkey

        # Call get_branch_details, this function get the branch details one by one
        get_branch_details $pkey $rkey

	done

done

# TODO: Add branch counter (Merged & totals)                                                                                                                                                                             
# TODO: Verify: With the key of json response of branch-details in one page (limit=5000 HAVE to TEST), we can iterate over the key to get the values ????
# TODO: Add Variables to extract other values.... reso_example = test_json.txt, example values: fromRef:repository:name, author, reviewers, 

# elapsed time with second resolution
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
eval "echo Elapsed time: $(date -ud "@$elapsed" +'$((%s/3600/24)) days %H hr %M min %S sec')"

echo -e "Files Generated: branches-details.txt"