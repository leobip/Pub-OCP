'''
##############################################
File: comp_Vers_lllp_v5.py
Project: Ocp_GetValues&Compare
Desc: 
File Created: Thursday, February 10th 2022, 5:30:50 pm
Author: Leoncio López (leobip27@gmail.com)
-----
Last Modified: Saturday, 14th May 2022 3:51:10 pm
Modified By: Leoncio López (leobip27@gmail.com>)
-----
Copyright <<projectCreationYear>> - 2022 Your Company, Your Company
################################################
'''


#####
# TWO Options for query pods
# oc describe pod name_pod
# oc get pod name_pod -o json
#####

#####
# Alternative to extract env variables
# oc set env pods --all --list  Obtain all pods env variables)
# oc set env pod/pod_name-x-xxxxx --list (specific pod env variables)
# oc set env dc/pod_name --list (specific pod - nombre generico)
#####

#####
# HELP
# Use -e parameter followed by the two enviroments to compare this env's in ocp or just one env without parameter to compare one env jenkinsfile with ocp
#####

from http.client import CONTINUE
import subprocess
import json
from sys import stdout
import re
import os
import sys
import git
import datetime
import shutil
from os import path
import stat
import prettytable
import getpass
from git import RemoteProgress


today = datetime.datetime.today()
date_key = str(today.date())

vers_pattern = '(\d.+)[^jar]'

###########################################################
# Ent			OCP			        GitHub(JenkinsFile)
# =====		==========   	        ===================
# dev_1     project-pre-1               prj/pre-1
# dev_2     project-pre-2               prj/pre-2
# pro       project-pro                 prj/pro
###########################################################

# Set the OCP Address
ocp_dev = 'https://url_dev_ocp:xxxx'
ocp_prod = 'https://url_prod:xxxx'

# GitHub Parameters:
username = 'user_github'
repo_url = 'git@github.xxx.xxxxxxx.xxxxxxxxx.corp:' + username + '/jenkinfiles_repo'
local_path = './temp-mercury-jenkins-repo/'

#####
# Common
#####

def params(env):
    # Parameters
    ocp_env = ''
    git_env = ''
    ocp_url = ''

    if env == 'dev_1':
        ocp_env = 'project-pre-1'
        git_env = 'prj/pre-1'
        ocp_url = ocp_dev

    elif env =='dev_2':
        ocp_env = 'project-pre-2'
        git_env = 'prj/pre-2'
        ocp_url = ocp_dev

    elif env =='pro':
        ocp_env = 'project-pro'
        git_env = 'prj/pro'
        ocp_url = ocp_prod

    else:
        print('\n##############################################')
        print('Wrong Arguments, please enter valid parameters: ')
        print('##############################################')
        print('dev_1: project-pre-1 - prj/pre-1')
        print('dev_2: project-pre-2 - prj/pre-2')
        print('pro: project-pro - prj/pro')
        print('')
        
        quit()

    return ocp_env, git_env, ocp_url

def split_art(art):
    splt = art.split(";")
    for x in range(len(splt)):
        splt[x] = os.path.basename(splt[x])

    return splt

def append_dict(file_name, json_to_append):
    dict_append = json.dumps(json_to_append)
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(dict_append)

    print(f"\nDatos del diccionario, han sido anexados al fichero: {file_name}\n")
    
    return

def compare_dicts(dict_1, dict_2, env, env_1, env_2, date_key):
    comp_dict = {}
    comp_dict[env] = {}
    dict_temp = {}
    
    # Extract Keys.
    # key_dict_1 = list(dict_1.keys())[0]
    # key_dict_2 = list(dict_2.keys())[0]

    for key in dict_1[env_1][date_key]:
        if (key == 'config-service'):
            continue

        try:
            if (dict_1[env_1][date_key][key]["ARTIFACT_URL"] == dict_2[env_2][date_key][key]["ARTIFACT_URL"]):
                compare = "=="
                artif = dict_2[env_2][date_key][key]["ARTIFACT_URL"][0]
            else:
                compare = dict_1[env_1][date_key][key]["ARTIFACT_URL"][0]
                artif = dict_2[env_2][date_key][key]["ARTIFACT_URL"][0]
        except:
            compare = dict_1[env_1][date_key][key]["ARTIFACT_URL"][0]
            artif = "N/D"

        try:
            if (dict_1[env_1][date_key][key]["CONFIG_ARTIFACT_URL"] == dict_2[env_2][date_key][key]["CONFIG_ARTIFACT_URL"]):
                compare_config = "=="
                config_artif = dict_2[env_2][date_key][key]["CONFIG_ARTIFACT_URL"][0]
            else:
                compare_config = dict_1[env_1][date_key][key]["CONFIG_ARTIFACT_URL"][0]
                config_artif = dict_2[env_2][date_key][key]["CONFIG_ARTIFACT_URL"][0]
        except:
            compare_config = dict_1[env_1][date_key][key]["CONFIG_ARTIFACT_URL"][0]
            if (compare_config == "null"):
                config_artif = "null"
            else:
                config_artif = "N/D"

        dict_temp[key] =  {"Vers-1": compare, "Vers-2": artif, "Config-1": compare_config, "Config-2": config_artif }
        comp_dict[env][date_key] = dict_temp

    # json.dump(comp_dict, open("compare_dict2.json", "w"))

    return comp_dict

def dict_to_screen(dict_to_print, env):
    for k, v in dict_to_print[env][date_key].items():
        compare = str(dict_to_print[env][date_key][k]["Vers-1"])
        version = str(dict_to_print[env][date_key][k]["Vers-2"])
        jenk_conf = str(dict_to_print[env][date_key][k]["Config-1"])
        ocp_conf = str(dict_to_print[env][date_key][k]["Config-2"])
        print("{:<30} {:<15} {:<25} {:<20} {:<20}".format(k, compare, version, jenk_conf, ocp_conf))

    return

def print_compare_conf(dict_to_print, env):
    print("\nCompare Configs JenkinsFiles / OCP: " + env + "\n")
    print("{:<30} {:<15} {:<20} {:<20} {:<20}".format('Artif.','Jenks.Vers','Ocp.Vers', 'Jenks.Config', 'Ocp.Config'))
    print("{:<30} {:<15} {:<20} {:<20} {:<20}".format('======.','=======','========', '===========', '=========='))

    dict_to_screen(dict_to_print, env)

    return

def print_compare_env(dict_to_print, env):
    print("\nCompare Enviroments: " + env + "\n")
    print("{:<30} {:<15} {:<20} {:<20} {:<20}".format('Artif.','Vers-1','Vers-2', 'Config-1', 'Config-2'))
    print("{:<30} {:<15} {:<20} {:<20} {:<20}".format('======.','=======','========', '=========', '========='))

    dict_to_screen(dict_to_print, env)

    return

def dict_to_text(comp_dict, env, header_0, header_1, header_2, header_3):

    with open('compare_report.txt', 'w') as f:
        f.write(header_0)
        f.write('\n' + header_1)
        f.write('\n' + header_2)
        f.write('\n' + header_3)

        for k, v in comp_dict[env][date_key].items():
            vers_1 = comp_dict[env][date_key][k]["Vers-1"]
            vers_2 = comp_dict[env][date_key][k]["Vers-2"]
            config_1 = str(comp_dict[env][date_key][k]["Config-1"])
            config_2 = str(comp_dict[env][date_key][k]["Config-2"])
            f.writelines("\n{:<30} {:<15} {:<25} {:<20} {:<20}".format(k + ',', vers_1 + ',', vers_2 +',', config_1 + ',', config_2))

    print("\nReporte guardado en: compare_report.txt")

    return

def report_config(comp_dict, env):

    header_0 = 'JenkinsFile / Ocp Compare Report: ' + env
    header_1 = 'Date: ' + date_key
    header_2 = ("{:<30} {:<15} {:<20} {:<20} {:<20}".format('Artif.','Jenks.Vers','Ocp.Vers', 'Jenks.Config', 'Ocp.Config'))
    header_3 = ("{:<30} {:<15} {:<20} {:<20} {:<20}".format('======.','=======','========', '==========', '=========='))
    
    dict_to_text(comp_dict, env, header_0, header_1, header_2, header_3)

    return

def report_env(comp_dict, env):

    header_0 = 'Compare OCP Enviroments Report: ' + env
    header_1 = 'Date: ' + date_key
    header_2 = ("{:<30} {:<15} {:<20} {:<20} {:<20}".format('Artif.','Vers-1','Vers-2', 'Config-1', 'Config-2'))
    header_3 = ("{:<30} {:<15} {:<20} {:<20} {:<20}".format('======.','=======','========', '==========', '========='))

    dict_to_text(comp_dict, env, header_0, header_1, header_2, header_3)

    return


#####
# OCP Section
#####
# TWO Options for query pods: oc describe pod name_pod  /  oc get pod name_pod -o json

def ocp_loggin(ocp_url, ocp_env):
    # cmd to get the token... in case we need later: oc whoami --show-token
    # Login OC

    usr_ocp = input("Please enter the login user to OCP: ")
    psw_ocp = getpass.getpass("Enter Password: ")
    args = 'oc login --username=' + usr_ocp + ' --password=' + psw_ocp + ' ' + ocp_url
    subprocess.call(args, shell=False)

    # Actvate Desire Project
    args = 'oc project ' + ocp_env
    subprocess.call(args, shell=False)

# Get Pod's List & save it in a list
def get_podslist():
    args = 'oc get pods'
    result = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
    lines = result.stdout.splitlines()

    # Use a RegExp to find the name of the pods from the 2nd line, delete the first line of the list, contains the headers
    # Add the Names of the pods to the list
    pattern_name = '^(\S+).*$'
    pattern_st = '^(?:\S+\s*){2}(\S+)'
    pattern_restarts = '^(?:\S+\s*){3}(\S+)'
    pods_list = []

    # Loop to extract the name, status, restarts
    for x in range(0, len(lines)):

        pods_restarts = re.findall(pattern_restarts, lines[x], re.MULTILINE)
        pods_st = re.findall(pattern_st, lines[x], re.MULTILINE)

        if pods_st[0] == 'Completed':
            continue

        pods_name = re.findall(pattern_name, lines[x], re.MULTILINE)

        pods_list.append(pods_name[0])
        pods_list.append(pods_st[0])
        pods_list.append(pods_restarts[0])

    return pods_list

# Get PODS params
def get_podsdetails(ocp_env, env, ocp_url):
    # prj = ocp prog / ent = to set the enviroment
    # Iterate over the list to get the config details of the pod

    ocp_loggin(ocp_url, ocp_env)
    pods_list = get_podslist()
    print("\nProcessing " + env + " . . . . .\n")
    pods_dict = {}
    pods_dict[env] = {}
    dict_temp = {}

    for x in range(3, len(pods_list), 3):
        
        args = 'oc get pod ' + pods_list[x] + ' -o json'
        result = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)
        podParams = json.loads(result.stdout)

        APP_NAME = ''
        ARTIFACT_URL = ''
        CONFIG_ARTIFACT_URL = ''
        CLASSPATH_ARTIFACT_URL = ''
        JAVA_OPT = ''

        # Loop to iterate over de json response to extract: APP_NAME (0), ARTIFACT_URL (1), CONFIG_ARTIFACT_URL (2), CLASSPATH_ARTIFACT_URL (3), JAVA_OPT (6)
        # In case of no value, (use of TRY)
        # Create a DICT and add the values by key = git_env
        ###############################################
        for n in range(7):
            if n == 4 or n == 5:
                continue

            try:
                name = podParams['spec']['containers'][0]['env'][n]['name']
            except:
                name = '########### NO-NAME ###########'
            
            try:
                value = podParams['spec']['containers'][0]['env'][n]['value']
            except:
                value = '########## NO-VALUE ###########'

            # Extract app_name
            if name == 'APP_NAME':
                APP_NAME = value

            # Extract file name from Artifasct_url
            elif name == 'ARTIFACT_URL':
                ARTIFACT_URL = os.path.basename(value)
                # Url complete: ARTIFACT_URL = value
                ARTIFACT_URL = re.findall(vers_pattern, ARTIFACT_URL, re.MULTILINE)

            # Extract Config_Artifact_url
            elif name == 'CONFIG_ARTIFACT_URL':

                CONFIG_ARTIFACT_URL = value.split(';')
                if (CONFIG_ARTIFACT_URL[0] != 'null'):
                    CONFIG_ARTIFACT_URL = os.path.basename(CONFIG_ARTIFACT_URL[0])
                    CONFIG_ARTIFACT_URL = re.findall(vers_pattern, CONFIG_ARTIFACT_URL, re.MULTILINE)

            # Extract Classpath_artifact_url
            elif name == 'CLASSPATH_ARTIFACT_URL':
                CLASSPATH_ARTIFACT_URL = value.split(';')
                for x in range(len(CLASSPATH_ARTIFACT_URL)):
                    CLASSPATH_ARTIFACT_URL[x] = os.path.basename(CLASSPATH_ARTIFACT_URL[x])
            
            # Extract java opts
            elif name == 'JAVA_OPT':
                JAVA_OPT = value
                JAVA_OPT = JAVA_OPT.split()
            
        # Create the App_Name Dict
        dict_temp[APP_NAME] = {}
        dict_temp[APP_NAME]['ARTIFACT_URL'] =  ARTIFACT_URL
        dict_temp[APP_NAME]['CONFIG_ARTIFACT_URL'] = CONFIG_ARTIFACT_URL
        dict_temp[APP_NAME]['CLASSPATH_ARTIFACT_URL'] = CLASSPATH_ARTIFACT_URL
        dict_temp[APP_NAME]['JAVA_OPT'] = JAVA_OPT

    # Verificar como montar los datos en campos ... tipo tabla 
    # puede ser pasando el pods_dict a una bd al final de la ejecucion    
    # json.dump(pods_dict, open("pods_dict.json", "w"))

    pods_dict[env][date_key] = dict_temp

    return pods_dict

def oc_logout():
    args = 'oc logout'
    subprocess.call(args, shell=False)


#####
# Query GITHUB / JenkinsFiles
#####

# This CLASS uses only for clone
class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)

# Clonar repo
def repo_clone(git_env):
    if (os.path.isdir(local_path)):
        local_path_git = local_path + '.git'

        if (os.path.isdir(local_path_git)):
            my_repo = git.Repo(local_path)
            local_branch = get_branch()

            if (git_env == local_branch):
                print("Local Repo exists, pulling to get the actual")
                my_repo.remotes.origin.pull()

            else:
                print("Local repo exists, checkout to desire branch & pull")
                my_repo.git.checkout(git_env)
                my_repo.remotes.origin.pull()
        
    else:
        print("Cloning Repository")
        git.Repo.clone_from(repo_url, local_path, branch = git_env, progress=CloneProgress())


# Get Repo Branch
def get_branch():
    my_repo = git.Repo(local_path)
    for branch in my_repo.branches:
        # print(branch)
        repo_branch = branch

# Checkout Branch & Pull
def repo_branch(git_env):
    repo_clone(git_env)
    # To Checkout to a different Branch & Pull
    # my_repo.git.checkout(git_env)
    # my_repo.remotes.origin.pull()

# Delete Local Repo ... Use after parse
def del_local_repo():
    for root, dirs, files in os.walk(local_path):

        for dir in dirs:
            os.chmod(path.join(root, dir), stat.S_IRWXU)

        for file in files:
            os.chmod(path.join(root, file), stat.S_IRWXU)

    shutil.rmtree(local_path)

# Get the local_repo file list & get the values with Jenkinsfiles Parser Funct
def jenkins_parser(git_env, env):
    repo_clone(git_env)
    repo_dir = local_path
    file_pattern = 'micro'

    APPLICATION_NAME = "APPLICATION_NAME=*'([^']*)'"
    ARTIFACT_URL= "ARTIFACT_URL=*'([^']*)'"
    CONFIG_ARTIFACT_URL= "CONFIG_ARTIFACT_URL=*'([^']*)'"
    CLASSPATH_ARTIFACT_URL = "CLASSPATH_ARTIFACT_URL=*'([^']*)'"

    JAVA_OPT_DEV = 'JAVA_OPT_DEV="([^"]*)"'
    JAVA_OPT_PRE = 'JAVA_OPT_PRE="([^"]*)"'
    JAVA_OPT_PRO = 'JAVA_OPT_PRO="([^"]*)"'

    jenkinsfile_dict = {}
    jenkinsfile_dict[env] = {}
    dict_temp = {}
    vers_pattern = '(\d.+)[^jar]'

    # iterate over the files 
    for filename in os.listdir(repo_dir):
        f = os.path.join(repo_dir, filename)
        # Check is file
        if os.path.isfile(f):

            if file_pattern in f:
                
                with open(f, 'r') as file_in:
                
                    read_f = file_in.read()

                    app_name = re.findall(APPLICATION_NAME, read_f, re.MULTILINE)
                   
                    art_url = re.findall(ARTIFACT_URL, read_f, re.MULTILINE)
                    art_url = os.path.basename(art_url[0])
                    art_url = re.findall(vers_pattern, art_url, re.MULTILINE)

                    conf_art_url = (re.findall(CONFIG_ARTIFACT_URL, read_f, re.MULTILINE))
                    if (conf_art_url[0] != 'null'):
                        conf_art_url = conf_art_url[0]
                        conf_art_url = conf_art_url.split(';')
                        conf_art_url = os.path.basename(conf_art_url[0])
                        conf_art_url = re.findall(vers_pattern, conf_art_url, re.MULTILINE)                       

                    clss_art_url = re.findall(CLASSPATH_ARTIFACT_URL, read_f, re.MULTILINE)
                    if (clss_art_url[0] != 'null'):
                        clss_art_url = split_art(clss_art_url[0])

                    try:
                        java_opt_pre = re.findall(JAVA_OPT_PRE, read_f, re.MULTILINE)
                        java_opt_pre = java_opt_pre[0].split()
                    except:
                        java_opt_pre = 'NO Settings'

                    try:
                        java_opt_pro = re.findall(JAVA_OPT_PRO, read_f, re.MULTILINE)
                        java_opt_pro = java_opt_pro[0].split()
                    except:
                        java_opt_pro = 'NO Settings'

                    try:
                        java_opt_dev = re.findall(JAVA_OPT_DEV, read_f, re.MULTILINE)
                        java_opt_dev = java_opt_dev[0].split()
                    except:
                        java_opt_dev = 'NO Settings'

                    dict_temp[app_name[0]] = {}
                    dict_temp[app_name[0]]['ARTIFACT_URL'] = art_url
                    dict_temp[app_name[0]]['CONFIG_ARTIFACT_URL'] = conf_art_url
                    dict_temp[app_name[0]]['CLASSPATH_ARTIFACT_URL'] = clss_art_url
                    dict_temp[app_name[0]]['JAVA_OPT_PRE'] = java_opt_pre
                    dict_temp[app_name[0]]['JAVA_OPT_PRO'] = java_opt_pro
                    dict_temp[app_name[0]]['JAVA_OPT_DEV'] = java_opt_dev


    jenkinsfile_dict[env][date_key] = dict_temp
    # TEST --- Save the Dict to Json file
    # json.dumps(jenkinsfile_dict, open("jenkins_dict.json"))

    return jenkinsfile_dict


#####
# MAIN
#####
def main():

    # # TEST SECTION - To activate, uncomment this lines & set the env. & points of debug
    # env = 'global'
    # ocp_env,git_env,ocp_url = params(env)
    # print("Comparacion de Config: " + env)
    # print("\nProcessing . . . . .\n")
    # # Get the config values in OCP 
    # pods_dict = get_podsdetails(ocp_env, env, ocp_url)
    # pods_file = 'pods_dict.txt'
    # append_dict(pods_file, pods_dict)
    # # Get the config values in Jenkinsfiles
    # jenkinsfile_dict = jenkins_parser(git_env, env)
    # jenks_file = 'jenkins_dict.txt'
    # append_dict(jenks_file, jenkinsfile_dict)
    # # Compare Dicts.
    # comp_dict = compare_dicts(jenkinsfile_dict, pods_dict, env, env, env, date_key)
    # comp_file = 'compare_dict.txt'
    # append_dict(comp_file, comp_dict)
    # # Print Results
    # print_compare_conf(comp_dict, env)
    # # Save Report in txt
    # report_config(comp_dict, env)
    # oc_logout()

    if sys.argv[1] == '-e':

        option = sys.argv[1]
        env_1 = sys.argv[2]
        env_2 = sys.argv[3]
        env = env_1 + '/' + env_2

        print("Comparación de Entornos OCP: " + env)

        ocp_env_1,git_env_1,ocp_url_1 = params(env_1)

        ocp_env_2,git_env_2,ocp_url_2 = params(env_2)

        print("\nProcessing . . . . .\n")

        # Get the config values in OCP - env_1
        pods_dict_1 = get_podsdetails(ocp_env_1, env_1, ocp_url_1)
        pods_file = 'pods_dict_1.txt'
        append_dict(pods_file, pods_dict_1)
        

        # Get the config values in OCP - env_1
        pods_dict_2 = get_podsdetails(ocp_env_2, env_2, ocp_url_2)
        pods_file = 'pods_dict_2.txt'
        append_dict(pods_file, pods_dict_2)

        # Compare Dicts
        env_comp = compare_dicts(pods_dict_1, pods_dict_2, env, env_1, env_2, date_key)

        # Print to Screen Results
        print_compare_env(env_comp, env)

        # Save to Text
        report_env(env_comp, env)

    
    elif sys.argv[1] == '-i':

        # Option to get only the config values from one env.
        print('This Option Get the values from one Env.')

        env_1 = sys.argv[2]
        ocp_env_1,git_env_1,ocp_url_1 = params(env_1)

        print("\nProcessing . . . . .\n")

        # Get the config values in OCP - env_1
        pods_dict_1 = get_podsdetails(ocp_env_1, env_1, ocp_url_1)
        pods_file = 'pods_dict_1.txt'
        append_dict(pods_file, pods_dict_1)

        print('Values Saved in ./pods_dict_1.txt')


    else:

        env = sys.argv[1]
        ocp_env,git_env,ocp_url = params(env)

        print("Comparacion de Config: " + env)

        print("\nProcessing . . . . .\n")

        # Get the config values in OCP 
        pods_dict = get_podsdetails(ocp_env, env, ocp_url)
        pods_file = 'pods_dict.txt'
        append_dict(pods_file, pods_dict)

        # Get the config values in Jenkinsfiles
        jenkinsfile_dict = jenkins_parser(git_env, env)
        jenks_file = 'jenkins_dict.txt'
        append_dict(jenks_file, jenkinsfile_dict)

        # Compare Dicts.
        comp_dict = compare_dicts(jenkinsfile_dict, pods_dict, env, env, env, date_key)
        comp_file = 'compare_dict.txt'
        append_dict(comp_file, comp_dict)

        # Print Results
        print_compare_conf(comp_dict, env)

        # Save Report in txt
        report_config(comp_dict, env)

    oc_logout()



if __name__ == "__main__":
    main()

