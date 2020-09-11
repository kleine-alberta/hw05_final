from django import forms
from django.forms import ModelForm, Textarea

from .models import Group, Post, Comment


class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(required=False,
                                   queryset=Group.objects.all(),
                                   empty_label=" ",
                                   label="Группа")
    text = forms.CharField(required=True,
                           widget=forms.Textarea,
                           help_text="Напишите свой абалденный пост тут!",
                           label="Текст")

    class Meta:
        model = Post
        fields = ("group", "text", "image")

    def clean_text(self):
        text = self.cleaned_data["text"]
        if text is None:
            raise forms.ValidationError(
                "поле должно быть заполнено"
            )
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widget = forms.Textarea(attrs={"rows": 10,
                                       "placeholder": "Ваш комментарий", })
