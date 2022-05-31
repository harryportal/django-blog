from django import forms
from .models import Comment


class EmailForm(forms.Form):
    name = forms.CharField(max_length=20)
    email = forms.EmailField()
    to = forms.EmailField()
    comment = forms.CharField(max_length=200, required=False, widget=forms.Textarea)


# building a form that is tied with a model
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name','email','body')