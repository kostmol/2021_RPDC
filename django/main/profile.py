from .models import *

def profileForm(user,cd):
    user.user_email = cd['user_email']
    user.apps_id = cd['apps_id']
    user.user_firstname = cd['user_firstname']
    user.user_lastname = cd['user_lastname']
    user.user_rank = cd['user_rank']
    user.save()

def metricsForm(user,cd):    
    user.user_scopus_id = cd['user_scopus_id']
    user.user_orc_id = cd['user_orc_id']
    user.user_scholar_id = cd['user_scholar_id']
    user.user_researcher_id = cd['user_researcher_id']
    user.save()

def app_author(user,scopus_author_API):
    user.citationcount = scopus_author_API.citationcount
    user.citedbycount = scopus_author_API.citedbycount
    user.coauthorcount = scopus_author_API.coauthorcount
    user.documentcount = scopus_author_API.documentcount
    user.hindex = scopus_author_API.hindex
    user.last_check = scopus_author_API.last_check
    user.last_update = scopus_author_API.last_update
    user.save()

    print('Author found in API and created')

def app_paper(user,scopus_paper_API):
    for paper in scopus_paper_API:
        # Papers.objects.update_or_create(scopus_id = paper.scopus_pid,
        #         author_id=paper.author_id,
        #         paper_type=paper.paper_type,
        #         paper_title=paper.title,
        #         paper_doi=paper.doi,
        #         paper_year=paper.pyear,
        #         paper_description=paper.description,
        #         paper_citedbycount=paper.citedbycount,
        #         paper_volume=paper.volume,
        #         paper_pages=paper.pages,
        #         publication_name = paper.publicationname,
        #         author_order = paper.author_order,
        #         paper_last_update=paper.last_update,
        #         paper_last_check=paper.last_check,)
            
    
        if Papers.objects.filter(scopus_id = paper.scopus_pid).exists():
            Papers.objects.filter(scopus_id = paper.scopus_pid).update(
                author_id=paper.author_id,
                paper_type=paper.paper_type,
                paper_title=paper.title,
                paper_doi=paper.doi,
                paper_year=paper.pyear,
                paper_description=paper.description,
                paper_citedbycount=paper.citedbycount,
                paper_volume=paper.volume,
                paper_eid = paper.eid,
                paper_pages=paper.pages,
                publication_name = paper.publicationname,
                author_order = paper.author_order,
                paper_last_update=paper.last_update,
                paper_last_check=paper.last_check,
            )
        else:
            Papers.objects.create(
                scopus_id = paper.scopus_pid,
                author_id=paper.author_id,
                paper_type=paper.paper_type,
                paper_title=paper.title,
                paper_doi=paper.doi,
                paper_year=paper.pyear,
                paper_description=paper.description,
                paper_citedbycount=paper.citedbycount,
                paper_volume=paper.volume,
                paper_eid = paper.eid,
                paper_pages=paper.pages,
                publication_name = paper.publicationname,
                author_order = paper.author_order,
                paper_last_update=paper.last_update,
                paper_last_check=paper.last_check,
            )

        print('Paper retrieved from API')

        p = Papers.objects.get(scopus_id = paper.scopus_pid)
        print(p)
        authorScopus(user,p)

def authorScopus(user,paper):
        AuthorScopus.objects.update_or_create(scopus_id = paper.paper_id, user_id = user.user_id)
