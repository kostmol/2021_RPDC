from formatS import bcolors, prog
import requests
import queries
import json
import time
# api docs
# https://dev.elsevier.com/api_docs.html

# quotas
# https://dev.elsevier.com/api_key_settings.html

# search
# https://www.scopus.com/search/form.uri?display=authorLookup#author

# https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl
# http://zhiyzuo.github.io/python-scopus/doc/quick-start.html

# Load configuration
con_file = open("./config/config.json")
config = json.load(con_file)
con_file.close()

# apiKey
apikey = config["apikey"]
# content to return
content = config["content"]

# api URIs
SEARCH_AUTHOR = "http://api.elsevier.com/content/search/author"
AUTHOR = "http://api.elsevier.com/content/author/author_id"
SCOPUS = "http://api.elsevier.com/content/search/scopus"

# Affiliation allias
AFFILS = ["International Hellenic University",
          "Alexander Technological Educational Institute of Thessaloniki",
          "School of Technological Applications"]

#
# Author search by name
#
def search_by_names(lastname, firstname, affil):
    # https://api.elsevier.com/content/search/author?query=AUTHLASTNAME(Sidiropoulos)AUTHFIRST(Antonis)AFFIL(International Hellenic University)
    par = {"apikey": apikey, "httpAccept": content,
           "query": "AUTHLASTNAME({})AFFIL({})".format(lastname, AFFILS[affil])}
    r = requests.get(SEARCH_AUTHOR, params=par)
    js = r.json()

    flag = False  # if is Found

    # if not found iterate trough all affiliation allias ("AFFILS" variable)
    if js["search-results"]["opensearch:itemsPerPage"] == "0":
        affil = affil + 1
    elif len(js["search-results"]["entry"]) >= 2:  # if query results > 1
        for i in js["search-results"]["entry"]:
            # first search with firstname
            if (firstname in i["preferred-name"]["given-name"].lower()) and flag == False:
                flag = True
                found(js, i)
            # if above false, search with affiliation name
            if ((firstname in i["preferred-name"]["given-name"].lower()) or AFFILS[affil] in i["affiliation-current"]["affiliation-name"]) and flag == False:
                flag = True
                found(js, i)
    else:
        for i in js["search-results"]["entry"]:
            flag = True
            found(js, i)
    if flag == False and affil <= len(AFFILS)-1:
        search_by_names(lastname, firstname, affil)
def found(js, i):
    auid = i["prism:url"].split("/")[-1]
    print(auid)
    get_author_by_auid(auid)


#
# Author search by scopus id
# https://api.elsevier.com/content/author/author_id/55918072400
#
def get_author_by_auid(auid):
    par = {"apikey": apikey, "httpAccept": content, "view": "enhanced"}
    r = requests.get("{}/{}".format(AUTHOR, auid), params=par)
    js = r.json()
    try:
        data = queries.authors(js, auid)
        queries.insertAuthor(data)
        print(bcolors.OKGREEN + auid + " inserted" + bcolors.ENDC)
        get_documents(auid)
    except Exception as e:
        print("{}, on get author: {}".format(e, auid))

#
# Documents
# https://api.elsevier.com/content/search/scopus?query=au-id(55918072400)&cursor=*&count=25
#
def get_documents(auid):
    currentCursor = '*'
    previousCursor = 1
    documentList = []
    coAuthorList = []
    while (previousCursor != currentCursor):
        par = {"apikey": apikey, "httpAccept": content,
               "query": "au-id({})".format(auid),
               "view":"complete",
               "cursor": currentCursor,
               "count": 25, }

        r = requests.get(SCOPUS, params=par)
        js = r.json()
        try:
            # cursor for json pagination
            currentCursor = js["search-results"]["cursor"]["@next"]
            previousCursor = js["search-results"]["cursor"]["@current"]
            if currentCursor != previousCursor:
                for i in js["search-results"]["entry"]:
                    data = queries.documents(i, auid)
                    # author order
                    authors = ""
                    if "author" in i:
                        for j in i["author"]:
                            authors = authors + j["authname"] + "|"
                            
                            # get co-author ids 
                            coauthor = queries.coAuthors(j)
                            coAuthorList.append(coauthor)
                            
                    authors = authors[:-1]
                    data = data + (authors,)
                    documentList.append(data)
        except Exception as e:
            print("{}, on get documents: {}".format(e, auid))
    queries.insertDocuments(documentList)
    print(bcolors.OKGREEN + "Documents inserted" + bcolors.ENDC)

    print(bcolors.WARNING +"Inserting author order and co-authors" + bcolors.ENDC)
    queries.insertCoAuthor(coAuthorList)
##

file2read = "./config/authors"
sumTime = 0
num_lines = sum(1 for line in open(file2read))
with open(file2read, "r") as names:
    for i, n in enumerate(names, start=1):
        inpt = n.split("\n")[0]
        if inpt.isnumeric():
            start = time.time()
            print("Search by auid {} {} ".format(inpt, prog(i, num_lines)))
            get_author_by_auid(inpt)

            end = time.time()
            fin = end - start
            sumTime = sumTime + fin
            print(bcolors.OKCYAN + "{}s for author {}".format(fin,inpt) + bcolors.ENDC)
        else:
            lastname = n.split(" ")[0].lower()
            firstname = n.split(" ")[1].lower()

            print("Search by f/lastname {} {}".format(firstname, lastname))
            search_by_names(lastname, firstname, 0)

print(bcolors.OKCYAN + "{}s for authors".format(sumTime) + bcolors.ENDC)
print(bcolors.OKCYAN + "{}s avg for author".format(sumTime/num_lines) + bcolors.ENDC)