from os import listdir
from os.path import isfile, join
import yaml


def GetFilesToSend(path, match):
    files = dict()
    for f in listdir(path):
        if isfile(join(path, f)):
            if f.find(match) >= 0:
                if f.find("~") == -1:
                    files[f] = join(path, f)
    return files


def GetAllFilesToSend(args):
    allFiles = []

    #########################################################################
    # DTSI files
    #########################################################################
    dtsiSlavesFile = args.dtsiPath+"slaves.yaml"
    uploadDir = "dtsi/"
    allFiles.append([dtsiSlavesFile, uploadDir])
    for slave in yaml.load(open(dtsiSlavesFile))['DTSI_CHUNKS']:
        dtsiFile = GetFilesToSend(args.dtsiPath+"hw/", slave+".")
        if len(dtsiFile) != 1:
            raise Exception(
                'Too few or too many dtsi file matches!\nret:{0}\n'.format(dtsiFile))
        for file in dtsiFile:
            uploadFile = uploadDir+file
            allFiles.append([dtsiFile[file], uploadFile])

    #########################################################################
    # Address table files
    #########################################################################
    tableSlavesFile = args.tablePath+"slaves.yaml"
    uploadFile = "address_table/slaves.yaml"
    allFiles.append([tableSlavesFile, uploadFile])
    tableYAML = yaml.load(open(tableSlavesFile))
    uploadXMLFileList = []
    for slave in tableYAML['UHAL_MODULES']:
        slave = tableYAML['UHAL_MODULES'][slave]
        if 'XML' in slave:
            for xmlFile in slave['XML']:
                if xmlFile not in uploadXMLFileList:
                    uploadXMLFileList.append([xmlFile, xmlFile])
    allFiles.extend(uploadXMLFileList)

    #########################################################################
    # FW files
    #########################################################################
    bitFiles = GetFilesToSend('bit/', 'top')
    for file in bitFiles:
        allFiles.append([bitFiles[file], file])

    return allFiles
