from django import forms
from django.contrib.auth.models import User

from evap.evaluation.models import Course, UserProfile
from evap.fsr.fields import UserModelMultipleChoiceField


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name_de', 'name_en', 'kind', 'study', 'vote_start_date', 'vote_end_date')
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        
        self.fields['kind'].widget.attrs['disabled'] = True
        self.fields['study'].widget.attrs['disabled'] = True
        
        self.fields['vote_start_date'].localize = True
        self.fields['vote_start_date'].widget = forms.DateInput()
        self.fields['vote_start_date'].widget.attrs['disabled'] = True
        
        self.fields['vote_end_date'].localize = True
        self.fields['vote_end_date'].widget = forms.DateInput()
        self.fields['vote_end_date'].widget.attrs['disabled'] = True
    
    def clean_kind(self):
        return self.instance.kind

    def clean_study(self):
        return self.instance.study

    def clean_vote_start_date(self):
        return self.instance.vote_start_date
    
    def clean_vote_end_date(self):
        return self.instance.vote_end_date


class UserForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField(required=False)
    
    proxies = UserModelMultipleChoiceField(queryset=User.objects.order_by("last_name", "username"))
    
    class Meta:
        model = UserProfile
        fields = ('title', 'first_name', 'last_name', 'email', 'picture', 'proxies')
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        
        # fix generated form
        self.fields['proxies'].required = False
        
        # load user fields
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email

    def save(self, *args, **kw):
        # first save the user, so that the profile gets created for sure
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        self.instance.user.email = self.cleaned_data.get('email')
        self.instance.user.save()
        self.instance = self.instance.user.get_profile()
        
        super(UserForm, self).save(*args, **kw)
