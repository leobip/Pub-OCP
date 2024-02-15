#!/bin/bash

# To calculate the elapsed time
start_time=$(date +%s)

### Testing curl's
#curl -k -H 'Authorization: Basic bHBlbGF5by5pdDpEbDIyI29jdDIyMDA=' -X GET -H "Content-type: application/json" https://bitbucket.hotelbeds.com/rest/api/1.0/projects?limit=2000
#curl -k -H 'Authorization: Basic bHBlbGF5by5pdDpEbDIyI29jdDIyMDA=' -X GET -H "Content-type: application/json" https://bitbucket.hotelbeds.com/rest/api/1.0/projects/ANS/repos?limit=2000
#curl -k -H 'Authorization: Basic bHBlbGF5by5pdDpEbDIyI29jdDIyMDA=' -X GET -H "Content-type: application/json" https://bitbucket.hotelbeds.com/rest/api/1.0/projects/ANS/repos/ansible/branches?base=refs%2Fheads%2Fmaster&details=true&limit=500

### Variables defined
bitbucket_url=https://bitbucket.hotelbeds.com
conten_type="Content-type: application/json"

### Delete the file generated in previous exec.
file="bitbucket-scan-results.csv"
if [ -f "$file" ] ; then
    rm "$file"
fi

# Delete previus execution log
file="scan-log.txt"
if [ -f "$file" ] ; then
    rm "$file"
fi

### Get the list of all the projects from Bitbucket account across all the pages
get_total_project_list () {

   	total_project_list=()

    response=$(curl -k -H "${auth_header}" -X GET -H "${content_type}" $bitbucket_url/rest/api/1.0/projects?limit=2000) 2>&1
	total_project_list=$(echo "${response}" | jq '.values[].key' | sed -e 's/"//g')

}


### Get the list of all repositories from each project listed above across the pages
get_total_repository_list() {
	echo ">>> Project is: $1"
	total_repo_list=()

    response=$(curl -k -H "${auth_header}" -X GET -H "${content_type}" $bitbucket_url/rest/api/1.0/projects/$1/repos?limit=2000) 2>&1

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
		response=$(curl -k -H "${auth_header}" -X GET -H "${content_type}" $bitbucket_url/rest/api/1.0/projects/$1/repos/$2'/branches?start='$start) 2>&1
		is_last_page=$(echo "${response}" | jq '.isLastPage')

        # use start only in case of no set limit.... because when use high limit & there is only one page ... the key: isLastPage no appear in the response
		start=$(echo "${response}" | jq '.nextPageStart')
        echo -e "START: $start"

        partial_branch_lists=$(echo "${response}" | jq '.values[].displayId')

		total_branch_list=("${total_branch_list[@]}" "${partial_branch_lists[@]}")

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
echo "PROJECT, REPOSITORY, BRANCH_NAME, MERGE, CREATED_DATE, UPDATED_DATE, CLOSED_DATE, MERGED_TO" > bitbucket-scan-results.csv

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
        # echo $pkey $rkey
		# get_branches_by_repository $pkey $rkey

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