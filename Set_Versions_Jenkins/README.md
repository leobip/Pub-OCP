# Excel File to Get Micros Version's from excel file, fill in Deploy/Table & Set in the respective JenkinsFile. 
# The Deploy/table can be done manually

## Files: 
    - setVersJenks.py
    - OcpVersionsJenkins.xlsm
    - SetVersJenkinsReport.txt
    - deploy_list_env_date.txt
    - deploy_table.xlsx
    - README

## The Excel file: 
    - Get the micros versions to deploy by parameters fill it in the main tab - Detailed Instructions in the page
    - The Deploy Table can be fill it manually too.
    - Reports: 
            - SetVersJenkinsReport.txt (values appended by run)
            - deploy_list_(ent)_(vers)_(date).txt - ex: deploy_list_dev_1.21.0_2022-04-26
    - Instructions to push the updated jenkinsfiles
            - Process in GitHub Desktop	(Your Choice)
	        - Add local Repository in File, Select the folder: temp-merc-jenks-repo 
	        - Verify the changes
	        - Add the Summary
	        - Press Commit
	        - Push the commit to GitHub


## Python Script:
    Running Options:
            - setVersJenks.py env vers
                - env: Enviroment
                - vers: Version of Relase or HotFix, to set in the report

Rev's:

27/04/2022
- Release
03/05/2022 - lllp
- Revisión excel file
14/05/2022
- Clean code - erase private vars
