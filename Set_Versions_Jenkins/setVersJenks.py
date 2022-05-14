'''
##############################################
File: setVersJenks.py
Project: Set_Versions_Jenkins
Desc: Script to import versions numbers from table in xls, clone the repository with jenkinsfiles & set the versions numbers in the 
in jenkinsfiles & print reports & deploy list
File Created: Saturday, 14th Feb 2022 3:44:46 pm
Author: Leoncio López (leobip27@gmail.com)
-----
Copyright <<projectCreationYear>> - 2022 Your Company, Your Company
################################################
'''


from asyncio.windows_events import NULL
from logging.config import dictConfig
import json
import re
import fileinput
import sys
import os
import pandas as pd
import datetime
import git
import shutil
from os import path
import stat
from git import RemoteProgress

# 21-04-2022 Added Class CloneProgress to repo_clone


today = datetime.datetime.today()
date_key = str(today.date())

# GitHub Parameters:
username = 'user_github'
repo_url = 'git@github.xxx.xxxxxxx.xxxxxxxxx.corp:' + username + '/jenkinfiles_repo'
local_path = './temp-mercury-jenkins-repo/'


# PATTERNS
ARTIF = "\\b(ARTIFACT_URL='[^']*')"
CONF_ARTIF = "\\b(CONFIG_ARTIFACT_URL='[^']*')"
# vers_pattern = '(\d.+)\/'
# vers_pattern = '(\d.+)[^jar]'
vers_pattern = '(\d.+).jar'

#####
# CLASSES
#####

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)


#####
# EXCEL
#####

def proc_excel(excel_file, env, deploy_vers):

    dict_excel = {}
    dict_excel[env] = {}
    dict_excel[env][date_key] = {}
    
    data_excel = pd.read_excel(excel_file, deploy_vers, engine='openpyxl')

    df = pd.DataFrame(data_excel, columns= ['Microservicios', 'Art', 'ArtifactId', 'Version', 'Deploy'])
    art = df.at[3,'ArtifactId']
    # print(df)

    for key, value in df.iterrows():

        if value['Deploy'] == 'YES':
            micro = value['Art']

            j_file = 'Jenkinsfile-micro-' + micro
            art = value['ArtifactId']
            vers = value['Version']

            # test Dict to verify if j_file exist... to add other micro to the same jenkinsfile, 
            # example: Jenkinsfile-micro-cloud	--- (cloud.config : 5.66.0 , cloud.web.all : 5.66.0)
            try:
                test_dict = dict_excel[env][date_key][j_file]
            except:
                dict_excel[env][date_key][j_file] = {}

            dict_excel[env][date_key][j_file][art] = {}
            dict_excel[env][date_key][j_file][art] = vers
            
        else:
            art = value['ArtifactId']
            vers = 'NO Desplegar'

    # To test the generated dict 
    # json.dump(dict_excel, open("dictexcel.json", "w"))

    return dict_excel


#####
# JENKINSFILES
#####

# Function to find the str & vers to change
def find_str(pipe_in, find_patt):

    pipe_in = local_path + pipe_in

    with open(pipe_in, 'r') as pipe_open:
        read_p = pipe_open.read()

        str_orig = re.findall(find_patt, read_p, re.MULTILINE)
        
        vers_orig = os.path.basename(str_orig[0])
        vers_orig = re.findall(vers_pattern, vers_orig, re.MULTILINE)
        
        vers_orig = vers_orig[0]
        str_orig = str_orig[0]

        pipe_open.close()

    return str_orig, vers_orig

# Function to replace string in pipeline
def replace_str(file_in, str_orig, vers_orig, vers_rep):

    file_in = local_path + file_in

    str_rep = str_orig.replace(vers_orig, vers_rep)

    for line in fileinput.input(file_in, inplace=1):

        line = line.replace(str_orig, str_rep)
        sys.stdout.write(line)

    return str_rep


#####
# Query GITHUB / JenkinsFiles
#####

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
        print("Cloning Repository...")
        git.Repo.clone_from(repo_url, local_path, branch = git_env, progress=CloneProgress())


# Get Repo Branch
def get_branch():
    my_repo = git.Repo(local_path)
    for branch in my_repo.branches:
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

    try:
        print("Erasing Old Clone...") 
        shutil.rmtree(local_path)
        print("\nTemp. Local Repo Erased.\n")

    except:
        pass


#####
# COMMON
#####

def params(env):
    # Parameters
    git_env = ''

    if env == 'dev_1':
        git_env = 'prj/pre-1'

    elif env =='dev_2':
        git_env = 'prj/pre-2'

    elif env =='pro':
        git_env = 'prj/pro'

    else:
        print('##############################################')
        print('Wrong Arguments, please enter valid parameters: ')
        print('##############################################')

    return git_env

#####
# MAIN
#####

def main():
    # Args...
    if sys.argv[1] == '-del':
        del_local_repo()

    else:
        env = sys.argv[1]
        vers = sys.argv[2]
        # Delete last local clone repo
        del_local_repo()

        # TEST 
        # env = 'dev'
        exl_tab = 'Deploy'

        # Clone Jenkins Repo
        git_env = params(env)
        repo_clone(git_env)

        # Process Excel
        print('\nAdjusting JenkinsFiles\n')
        excel_file = '.\OcpVersionsJenkins.xlsm'
        dict_rep = proc_excel(excel_file, env, exl_tab)

        # Reports
        report_file = '.\SetVersJenkinsReport.txt'
        with open(report_file, 'a') as f:
            f.write('\n#######################\n')
            f.write('Report Date: ' + date_key +'\n')
            f.write('Enviroment: ' + env + '\n')
            f.write('#######################')
        
        deploy_list = '.\deploy_list_' + env + '_' + vers + '_' +date_key + '.txt'

        j_file_prev = ''
        
        # Iterate over dict_rep from excel file & replace values in jenkinsfiles
        for k in dict_rep[env][date_key].items():
            
            j_file = k[0]
            # Add microservice name to deploy_list_(date).txt
            if j_file != j_file_prev:

                with open(deploy_list,'a') as f:
                    f.write(j_file + '\n')
            
                with open(report_file, 'a') as f:
                    f.write('\nJenkinsFile: ' + j_file + '\n')

            rep_values = k[1]

            for i in rep_values:
                artifact_name = i
                vers_replace = rep_values[i]

                if (artifact_name.find('config') == -1):
                    PATT_REP = ARTIF           
                else:
                    PATT_REP = CONF_ARTIF
                
                str_orig, vers_orig = find_str(j_file, PATT_REP)

                str_replaced = replace_str(j_file, str_orig, vers_orig, vers_replace)

                # añadir la cadena original y de reemplazo a un fichero de text
                with open(report_file, 'a') as f:

                    #f.write('String Original: ' + str_orig + '\n')
                    f.write('Version Original: ' + vers_orig + '\n')
                    f.write('Version Replaced: ' + vers_replace + '\n')
                    f.write('String Replaced: ' + str_replaced + '\n')

            j_file_prev = j_file

        print('\nVersions updated in the jenkinsfiles...\n')
        print('########################################')
        print('Deploy List: ' + deploy_list + '\n')
        print('########################################')
        print('Report Updated: ' + report_file + '\n')

        # Pendiente Diff
        # Pendiente el PUSH
        # Alternativa ... despues de agregar el repo como repo local a github desktop, Verificar las modificaciones, hacer el commit & Push
        # Pendiente:  ... agregar funcion para desconectarlo de la app y borrarlo


if __name__ == "__main__":
    main()
