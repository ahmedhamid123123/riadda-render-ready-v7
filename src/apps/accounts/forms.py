from django import forms
from .models import User

class AgentCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'AGENT'
        if commit:
            user.save()
        return user
