#!/bin/env python
import argparse
from git import Repo  # interact with local git repo
import re  # decode local repo
import requests  # interact with github.com
import json  # parse github return
import os
import yaml
from getFiles import GetAllFilesToSend  # find files


token = ""


def releaseFile(releaseJSON, localFile, uploadFile):
    global token
    url = releaseJSON["upload_url"].replace(
        "{?name,label}", "?name="+uploadFile)
    uploadFile = open(localFile)
    response = requests.post(url, data=uploadFile, headers={
                             "Authorization": "token "+token, "Content-Type": "application/octet-stream"})
    uploadFile.close()
    if response.status_code != 201:
        raise Exception('Error ({0}:{1}) while uploading {2}\n{3}'.format(
            response.status_code, response.reason, localFile, response.text))


def main():
    parser = argparse.ArgumentParser(description="Build address table.")
    parser.add_argument("--dtsiPath", "-d", help="path for dtsi files")
    parser.add_argument("--tablePath", "-t",
                        help="path for address table files")
    args = parser.parse_args()

    # get the token for remote write access to the repo
    global token
    token=os.getenv("GH_TOKEN")
    if token == None:
        print "Missing github oath token"
        quit()

    #############################################################################
    # Load local repo and
    #############################################################################

    # open current path as repo
    localRepo = Repo("./")
    localRepoRemote=localRepo.remotes.origin.url
    # get remote info
    # match git@HOST:XXXXX or https://HOST:XXXX
    host=   re.search('(\@|https:\/\/)(.*):',localRepoRemote).group(2)
    # match XXXXhost:PROJECT/XXXXX
    project=re.search('(\@|https:\/\/).*:(.*)\/',localRepoRemote).group(2)
    # match XXXXhost:project/REPO.git
    repo=   re.search('(\@|https:\/\/).*:.*\/(.*).git',
                      localRepoRemote).group(2)

    print "Repo is "+host+"/"+project+"/"+repo

    # get branch and check that it is a release branch
    branch=localRepo.active_branch.name
    # check if this is named release
    releaseVersion=""
    if branch.find("release-v") >= 0:
        releaseVersion=branch[branch.find("release-v") + len("release-v"):]
    elif branch.find("hotfix-v") >= 0 :
        releaseVersion=branch[branch.find("hotfix-v") + len("hotfix-v"):]
    else:
        print "Not on a release or hotfix branch!"
        quit()

    print "Release:"+ releaseVersion


    #############################################################################
    # Create a new release remotely
    #############################################################################

    # Create the new release
    GIT_API_URL="https://api."+host+"/repos/"+project+"/"+repo+"/releases"

    createReleaseData='\
        {\
    	"tag_name": "v'+releaseVersion+'",\
    	"target_commitish": "'+branch+'",\
    	"name": "v'+releaseVersion+'",\
    	"body": "v '+releaseVersion+' release of '+repo+'",\
    	"draft": false,\
    	"prerelease": false\
    	}'

    response=requests.post(GIT_API_URL,data=createReleaseData,headers = {
                           "Authorization": "token "+token})
    if response.status_code != 201:
        print "Error: Creation failed with {0}".format(response.status_code)
        quit()
    else:
        print "Created draft release v{0}".format(releaseVersion)
    ReleaseJSON=json.loads(response.text)

    #############################################################################
    # Upload files to the release
    #############################################################################

    try:
        allFiles = GetAllFilesToSend(args)
        padding = 0
        for item in allFiles:
            if len(item[0]) > padding:
                padding = len(item[0]) + 1
        for item in allFiles:
            print "  Uploading:", (item[0]).ljust(
                padding), "to", item[1]
            releaseFile(ReleaseJSON, item[0], item[1])
    except Exception as e:
        requests.delete(ReleaseJSON["url"], headers={
                        "Authorization": "token "+token})
        requests.delete("https://api."+host+"/repos/"+project+"/"+repo+"/git/refs/tags/" +
                        ReleaseJSON["tag_name"], headers={"Authorization": "token "+token})
        print "Error! Deleting partial release"
        print e


if __name__ == "__main__":
    main()
