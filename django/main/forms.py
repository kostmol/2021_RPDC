from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *


class NewUserForm(UserCreationForm):
    # email = forms.EmailField(required=True))
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        # user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class AuthorForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(AuthorForm, self).__init__(*args, **kwargs)
    class Meta:
        model = AppUser

        fields = ('user_email', 'user_firstname', 'user_lastname','apps_id', 'user_rank', 'user_scopus_id','user_orc_id','user_scholar_id','user_researcher_id')

        labels = {
            'user_email': 'Email address',
            'user_firstname': 'First Name',
            'user_lastname': 'Last Name',
            'user_rank': 'Rank',
            'apps_id': 'Apps ID',
            'user_scopus_id': 'Scopus ID',
            'user_orc_id': 'ORC ID',
            'user_scholar_id': 'Scholar ID',
            'user_researcher_id': 'Researcher ID',
        }

