import mysql.connector
import sshtunnel
import json
import pandas as pd
from datetime import datetime
from formatS import bcolors
import time

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

# load config
con_file = open("./config/config.json")
config = json.load(con_file)
con_file.close()

sshHostname = config["sshHost"]
sshUsername = config["sshUser"]
sshPassword = config["sshPass"]
#


def q_execute(statement, data):  # connect to mysql over ssh
    with sshtunnel.SSHTunnelForwarder(
        (sshHostname),
        ssh_username=sshUsername, ssh_password=sshPassword,
        remote_bind_address=('127.0.0.1', 3306)
    ) as tunnel:
        connection = mysql.connector.connect(
            user=sshUsername, password=sshPassword,
            host='127.0.0.1', port=tunnel.local_bind_port,
            database='RPDC', autocommit=True
        )
        cursor = connection.cursor()

        if len(data) == 1:
            cursor.execute(statement, data[0])
        else:
            start = time.time()
            cursor.executemany(statement, data)
            end = time.time()
            print(end-start,"ms for SQL")


def insertAuthor(data):
    statement = (
        """insert into scopus_author (scopus_auid, orcID, lastname, firstname, hindex, DocumentCount, CoauthorCount, CitedByCount, CitationCount, last_check)
        values (%s,%s,%s, %s,%s,%s, %s,%s,%s, %s)
        ON DUPLICATE KEY UPDATE
        orcID = values(orcID),
        lastname = values(lastname),
        firstname = values(firstname),
        hindex = values(hindex),
        DocumentCount = values(DocumentCount),
        CoauthorCount = values(CoauthorCount),
        CitedByCount = values(CitedByCount),
        CitationCount = values(CitationCount),
        last_update = now()
    """)
    try:
        q_execute(statement, [data])
    except mysql.connector.Error as err:
        print(err)
        pass


def insertDocuments(data):
    statement = (
        """insert into scopus_paper (scopus_pid, author_id, title, creator,description, doi, pyear, 
        p_type, CitedByCount, pages, volume, source_id, affiliation_name, affiliation_city, affiliation_country, last_check)
        values (%s,%s,%s, %s,%s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        author_id = values(author_id),
        title = values(title),
        creator = values(creator),
        description = values(description),
        doi = values(doi),
        pyear = values(pyear),
        p_type = values(p_type),
        CitedByCount = values(CitedByCount),
        pages = values(pages),
        volume = values(volume),
        source_id = values(source_id),
        affiliation_name = values(affiliation_name),
        affiliation_city = values(affiliation_city),
        affiliation_country = values(affiliation_country),
        last_update = now()
    """)
    try:
        q_execute(statement, data)
    except mysql.connector.Error as err:
        print(err)
        pass


def insertPaperAuthor(data):
    statement = (
        """insert into scopus_paper_author (scopus_pid, scopus_auid, scopus_author_order)
        values (%s,%s,%s)
        ON DUPLICATE KEY UPDATE
        scopus_auid = values(scopus_auid),
        scopus_author_order = values(scopus_author_order)

    """)
    try:
        q_execute(statement, data)
    except mysql.connector.Error as err:
        print(err)
        pass


def insertCoAuthor(data):
    statement = (
        """insert ignore into scopus_author(scopus_auid,orcID,lastname,firstname)
        values (%s,%s,%s,%s)
    """)
    try:
        q_execute(statement,data)
    except mysql.connector.Error as err:
        print(err)
        pass

# JSON search filters


def documents(i, auid):
    author_id = auid
    title = i["dc:title"]
    sourceId = i["source-id"]
    pyear = i["prism:coverDate"]
    description = i["dc:description"] if "dc:description" in i else None
    citedbyCount = i["citedby-count"]
    paper_type = i["prism:aggregationType"]
    scopus_pid = i["dc:identifier"].split(":")[1]
    doi = i["prism:doi"] if "prism:doi" in i else None
    creator = i["dc:creator"] if "dc:creator" in i else None
    volume = i["prism:volume"] if "prism:volume" in i else None
    pages = i["prism:pageRange"] if "prism:pageRange" in i else None
    affilName = i["affiliation"][0]["affilname"] if "affiliation" in i else None
    affilCity = i["affiliation"][0]["affiliation-city"] if "affiliation" in i else None
    affilCountry = i["affiliation"][0]["affiliation-country"] if "affiliation" in i else None
    lastcheck = datetime.now()

    data = (scopus_pid, author_id, title, creator, description, doi, pyear, paper_type,
            citedbyCount, pages, volume, sourceId, affilName, affilCity, affilCountry, lastcheck)
    return data


def authors(js, auid):
    orcid = js["author-retrieval-response"][0]["coredata"]["orcid"] if "orcid" in js["author-retrieval-response"][0]["coredata"] else None
    firstname = js["author-retrieval-response"][0]["author-profile"]["preferred-name"]["given-name"]
    lastname = js["author-retrieval-response"][0]["author-profile"]["preferred-name"]["surname"]
    citationCount = js["author-retrieval-response"][0]["coredata"]["citation-count"]
    citedbyCount = js["author-retrieval-response"][0]["coredata"]["cited-by-count"]
    docCount = js["author-retrieval-response"][0]["coredata"]["document-count"]
    coauthorCount = js["author-retrieval-response"][0]["coauthor-count"]
    hindex = js["author-retrieval-response"][0]["h-index"]
    lastcheck = datetime.now()

    data = (auid, orcid, lastname, firstname, hindex, docCount,
            coauthorCount, citedbyCount, citationCount, lastcheck)
    return data
###


def coAuthors(js):
    authid = js["authid"]
    orcid = js["orcid"] if "orcid" in js else None
    firstname = js["given-name"]
    lastname = js["surname"]
    data = (authid, orcid, firstname, lastname)
    return data
