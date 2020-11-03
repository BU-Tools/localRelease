from os import listdir
from os.path import isfile, join
import yaml

def GetFilesToSend(path,match):
    files=dict()
    for f in listdir(path):
        if isfile(join(path,f)):
            if f.find(match) >= 0:
                if f.find("~") == -1:
                    files[f]=join(path,f)
    return files


def GetAllFilesToSend(args):
    allFiles = []

    dtsiSlavesFile=args.dtsiPath+"slaves.yaml"
    allFiles.append(dtsiSlavesFile)

    for slave in yaml.load(open(dtsiSlavesFile))['DTSI_CHUNKS']:
        dtsiFile=GetFilesToSend(args.dtsiPath+"hw/",slave+".")    
        for file in dtsiFile:
            allFiles.append(dtsiFile[file])

    tableSlavesFile=args.tablePath+"slaves.yaml"
    allFiles.append(tableSlavesFile)

    tableYAML = yaml.load(open(tableSlavesFile))
    uploadXMLFileList=[]
    for slave in tableYAML['UHAL_MODULES']:
        slave = tableYAML['UHAL_MODULES'][slave]
        if 'XML' in slave:
            for xmlFile in slave['XML']:
                if xmlFile not in uploadXMLFileList:
                    uploadXMLFileList.append(xmlFile)
    allFiles.extend(uploadXMLFileList)

    bitFiles=GetFilesToSend('bit/','top')
    for file in bitFiles:
        allFiles.append(bitFiles[file])

    return allFiles