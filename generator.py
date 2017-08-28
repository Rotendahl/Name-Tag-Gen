import csv, os
from jinja2 import Template
from subprocess import call
from PyPDF2 import PdfFileMerger
import sys

if len(sys.argv) != 2:
    print("Error \nUsage: generator.py file.csv ")



""" Setup """
nrOfGroups = 3
nrOfSubgroups = 13
groups = []
html = open('template.html', 'r').read()
call(["rm", "-rf", "groups"])
call(["rm", "-rf", "output"])
os.mkdir("output")
os.mkdir("groups")
for i in range(nrOfGroups):
    groups.append([])


"""
    Reads and organizes the names file such that "group" has the structure
    [trip1, trip2, ... ,tripn], where trip_i has the structure:
    [[{names: [], subGroupNr], [{names: [], subGroupNr] }]
"""
with open(sys.argv[1],'r') as csvFile:
    reader = csv.DictReader(csvFile)
    for row in reader:
        group = int(row['group'])
        subGroupNr = int(row['subgroup'])
        isCreated = False
        for subgroup in groups[group]:
            if subgroup['nr'] == subGroupNr:
                subgroup['names'].append(row['name'])
                isCreated = True
        if not isCreated:
            groups[group].append({'names' : [row['name']], 'nr' : subGroupNr })



""" Givin a file name and the name of 8 people and a logo it creates a page """
def createPage(outFile, names, logoFile):
    data = {'names': names, 'logo': logoFile}
    template = Template(html)
    with open(outFile, 'w') as out:
        out.write(template.render(data))


def mergePdfs(outfile, pdfs):
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))
    with open(outfile, 'wb') as fout:
        merger.write(fout)


def createSubGroup(group, groupNr):
    groupDir = "groups/" + "group-" + str(groupNr)
    os.mkdir(groupDir)
    pageNr = 0
    for subgroup in group:
        currentPage = []
        subdir = groupDir + "/subgroup-" + str(subgroup['nr'])
        os.mkdir(subdir)
        for i in range(len(subgroup['names'])):
            currentPage.append(subgroup['names'][i])
            if len(currentPage) == 8 or i == len(subgroup['names'])-1:
                fileName = "/page" + str(pageNr) + ".html"
                logo = "../../../logos/logo" +str(groupNr) + ".png"
                createPage(subdir + fileName, currentPage, logo)
                currentPage = []
                pageNr += 1
        pages = os.listdir(subdir)
        i = 0
        for page in pages:
            htmlFile = subdir + "/" + page
            pdfFile = subdir + "/page" + str(i) + ".pdf"
            i += 1
            call(["html-pdf", htmlFile, pdfFile])
            status = "Did group "+ str(groupNr)+" subgroup "+str(subgroup['nr'])
            print(status + " page " + str(i))

        files = os.listdir(subdir)
        pdfs = []
        for fil in files:
            if ".pdf" in fil:
                pdfs.append(subdir + "/" + fil)
        name = "output/" + "Tur" + str(groupNr)
        name += "-hold" + str(subgroup['nr']) + ".pdf"
        mergePdfs(name, pdfs)


for i in range(len(groups)):
    createSubGroup(groups[i], i)

call(["rm", "-rf", "groups"])
print("Done!")
