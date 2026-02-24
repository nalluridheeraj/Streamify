from django import forms
from .models import Content, Comment, Genre


class ContentUploadForm(forms.ModelForm):
    genre = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Content
        fields = [
            'title',
            'description',
            'content_type',
            'file_path',
            'thumbnail',
            'genre',
            'artist_name',
            'album',
            'is_published',
            'is_premium'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'file_path': forms.FileInput(attrs={'class': 'form-control', 'accept': 'audio/*,video/*'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'artist_name': forms.TextInput(attrs={'class': 'form-control'}),
            'album': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['file_path'].required = False
            self.fields['thumbnail'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...'
            })
        }