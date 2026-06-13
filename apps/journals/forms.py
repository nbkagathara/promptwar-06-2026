from django import forms
from apps.journals.models import JournalEntry


class JournalEntryForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Write your thoughts, feelings, study experiences, or exam concerns here...",
            }
        ),
        label="Daily Reflection",
    )

    class Meta:
        model = JournalEntry
        fields = ["content"]
