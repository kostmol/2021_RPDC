from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# TEST MODELS
class ScopusAuthor(models.Model):
    scopus_auid = models.PositiveBigIntegerField(primary_key=True)
    orcid = models.CharField(db_column='orcID', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(max_length=200, blank=True, null=True)
    firstname = models.CharField(max_length=200, blank=True, null=True)
    hindex = models.PositiveIntegerField(blank=True, null=True)
    documentcount = models.PositiveBigIntegerField(db_column='DocumentCount', blank=True, null=True)  # Field name made lowercase.
    coauthorcount = models.PositiveBigIntegerField(db_column='CoauthorCount', blank=True, null=True)  # Field name made lowercase.
    citedbycount = models.PositiveBigIntegerField(db_column='CitedByCount', blank=True, null=True)  # Field name made lowercase.
    citationcount = models.PositiveBigIntegerField(db_column='CitationCount', blank=True, null=True)  # Field name made lowercase.
    last_update = models.DateTimeField(blank=True, null=True)
    last_check = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'scopus_author'

    # def __str__(self):
    #     return str(self.scopus_auid)

class ScopusPaper(models.Model):
    scopus_pid = models.PositiveBigIntegerField(primary_key=True)
    author_id = models.BigIntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    doi = models.CharField(max_length=100, blank=True, null=True)
    pyear = models.SmallIntegerField(blank=True, null=True)
    paper_type = models.CharField(max_length=21, blank=True, null=True)
    citedbycount = models.PositiveIntegerField(db_column='CitedByCount')  # Field name made lowercase.
    pages = models.CharField(max_length=45, blank=True, null=True)
    volume = models.CharField(max_length=45, blank=True, null=True)    
    eid = models.CharField(max_length=100, blank=True, null=True)
    publicationname = models.TextField(db_column='publicationName', blank=True, null=True)  # Field name made lowercase.
    author_order = models.CharField(max_length=255, blank=True, null=True)
    affiliation_name = models.CharField(max_length=100, blank=True, null=True)
    affiliation_city = models.CharField(max_length=100, blank=True, null=True)
    affiliation_country = models.CharField(max_length=100, blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    last_check = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    paper_type = models.CharField(max_length=21, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'scopus_paper'

    def __str__(self):
        return str(self.scopus_pid)

class ScopusPaperAuthor(models.Model):
    scopus_pid = models.OneToOneField(ScopusPaper, models.DO_NOTHING, db_column='scopus_pid', primary_key=True)
    scopus_auid = models.ForeignKey(ScopusAuthor, models.DO_NOTHING, db_column='scopus_auid')
    scopus_author_order = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'scopus_paper_author'
        unique_together = (('scopus_pid', 'scopus_author_order'), ('scopus_auid', 'scopus_pid'),)

    # def __str__(self):
    #     return self.scopus_pid

# null - Allows column to keep null value.
# default - Default value for cell
# blank - Will be used only if Forms for validation and not related to the database.


# APP MODELS
class AppUser(models.Model):
    class Ranks(models.TextChoices):
        ACADEMIC_FELLOW = "Academic Fellow"
        ADJUNCT = "Adjunct Professor"
        ADMIN_STAFF = "Administrative Staff"
        ASSISTANT = "Assistant Professor"
        ASSOSIATE = "Associate Professor"
        ETP = "ETP"
        FORMER_FAC_EMER = "Former Faculty/Emeritus"
        GUEST = "Guest Professors"
        LAB_ASSOC = "Laboratory Associate"
        LAB_STAFF = "Laboratory Teaching Staff"
        LECTURER = "Lecturer"
        LECTURER_PA = "Lecturer by PA"
        PD407 = "PD407"
        PROFESSOR = "Professor"
        PROFESSOR_MSC= "Professor at MSc"
        SECRETARY= "Secretary"    

    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True)
    user_email = models.EmailField(max_length=255, blank=True, null=True)
    user_firstname = models.CharField(max_length=255, blank=True, null=True)
    user_lastname = models.CharField(max_length=255, blank=True, null=True)
    user_rank = models.CharField(max_length=100, choices=Ranks.choices, blank=True, null=True)
    apps_id = models.IntegerField(blank=True,null=True)
    user_scopus_id = models.BigIntegerField(blank=True, null=True)
    user_orc_id = models.CharField(max_length=100,blank=True, null=True)
    user_scholar_id = models.PositiveIntegerField(blank=True, null=True)
    user_researcher_id = models.PositiveIntegerField(blank=True, null=True)

    hindex = models.PositiveIntegerField(blank=True, null=True)
    documentcount = models.PositiveBigIntegerField(blank=True, null=True)
    coauthorcount = models.PositiveBigIntegerField(blank=True, null=True)
    citedbycount = models.PositiveBigIntegerField(blank=True, null=True)
    citationcount = models.PositiveBigIntegerField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    last_check = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username

# class Author(models.Model):
    #     author = models.ForeignKey(AppUser, models.CASCADE,null=True, related_name='authors')
    #     scopus_auid = models.PositiveBigIntegerField(primary_key=True)
    #     orcid = models.CharField(max_length=100, blank=True, null=True)
    #     firstname = models.CharField(max_length=200, blank=True, null=True)
    #     lastname = models.CharField(max_length=200, blank=True, null=True)
    #     hindex = models.PositiveIntegerField(blank=True, null=True)
    #     documentcount = models.PositiveBigIntegerField(blank=True, null=True)
    #     coauthorcount = models.PositiveBigIntegerField(blank=True, null=True)
    #     citedbycount = models.PositiveBigIntegerField(blank=True, null=True)
    #     citationcount = models.PositiveBigIntegerField(blank=True, null=True)
    #     last_update = models.DateTimeField(blank=True, null=True)
    #     last_check = models.DateTimeField(blank=True, null=True)

class Papers(models.Model):
    author_id = models.BigIntegerField(blank=True, null=True)
    # author_id = models.ForeignKey(AppUser, models.DO_NOTHING,null=True)
    paper_id = models.AutoField(primary_key=True)
    scopus_id = models.BigIntegerField(blank=True, null=True)
    paper_type = models.CharField(max_length=21, blank=True, null=True)
    paper_title = models.CharField(max_length=255, blank=True, null=True)
    paper_doi = models.CharField(max_length=100, blank=True, null=True)
    paper_year = models.SmallIntegerField(blank=True, null=True)
    paper_description = models.TextField(blank=True, null=True)
    paper_citedbycount = models.PositiveIntegerField(blank=True, null=True)
    paper_volume = models.CharField(max_length=45, blank=True, null=True)
    paper_eid = models.CharField(max_length=100, blank=True, null=True)
    paper_pages = models.CharField(max_length=45, blank=True, null=True)
    author_order = models.CharField(max_length=255, blank=True, null=True)
    publication_name = models.TextField(blank=True, null=True)
    paper_last_update = models.DateTimeField(blank=True, null=True)
    paper_last_check = models.DateTimeField(blank=True, null=True)

    def get_year(self):
        return self.paper_year.year
        
    def count(self):
        return self.paper_title
        
    def __str__(self):
        return str(self.paper_id)
        
# # sid = models.AutoField(default=None)
class AuthorScopus(models.Model):
    scopus = models.ForeignKey(Papers, on_delete = models.CASCADE)
    user = models.ForeignKey(AppUser, on_delete = models.DO_NOTHING)

    class Meta:
        unique_together = ('scopus', 'user')