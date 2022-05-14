# Script to Get Values from OCP-Pod's Config, Jenkinsfiles, & compare.
The script: 
    - Download the jenkinsfiles and store the values in a dict
    - Connect to OCP and the project's selected and get config values & store it in a dict
    - Compare the values & print it in report: 
                    - ARTIFACT_URL
                    - CONFIG_ARTIFACT_URL
                
Options:
    - To Compare (2) two env's from OCP: -e env_1 env_2 

    - To Compare Jenkinsfiles with the respective deployed running micro in OCP: env

    - To Get the values from one env in OCP: -i env_1

Examples:
    - Txt´s files

Rev's:

20/04/2022
- Update ocp4 (Cert) Address
- Added user & password functions to the OCP login - password with getpass() module

13/05/2022
- Added Global enviroment
- Deleted JAVA_OPT = JAVA_OPT_XXX by env Section 
- Added JAVA_OPT_PRE, JAVA_OPT_PRO & JAVA_OPT_DEV parse to the json report.
- Added RemoteProgress Class - To print repository download progress
- Clean Import Section
- Generated v5.

14/05/2022
- Clean code .... 
- Remove innecesary returns


