from django import forms
from apps.moods.models import MoodLog


class MoodLogForm(forms.ModelForm):
    MOOD_CHOICES = [
        ("1", "1 - Very Low / Depressed"),
        ("2", "2 - Low / Anxious"),
        ("3", "3 - Neutral / Okay"),
        ("4", "4 - Good / Happy"),
        ("5", "5 - Excellent / Energetic"),
    ]
    STRESS_CHOICES = [
        ("1", "1 - No Stress / Calm"),
        ("2", "2 - Low Stress"),
        ("3", "3 - Moderate / Manageable"),
        ("4", "4 - High Stress / Heavy"),
        ("5", "5 - Extreme Stress / Overwhelmed"),
    ]
    ENERGY_CHOICES = [
        ("1", "1 - Exhausted / Low"),
        ("2", "2 - Tired / Sluggish"),
        ("3", "3 - Normal / Steady"),
        ("4", "4 - High Energy"),
        ("5", "5 - Peaked / Very Active"),
    ]
    SLEEP_CHOICES = [
        ("1", "1 - Terrible / Restless"),
        ("2", "2 - Poor Sleep"),
        ("3", "3 - Average / Sufficient"),
        ("4", "4 - Good Rest"),
        ("5", "5 - Deep / Restorative"),
    ]
    STUDY_CHOICES = [
        ("1", "1 - Highly Unsatisfied"),
        ("2", "2 - Disappointed"),
        ("3", "3 - Acceptable / Progressing"),
        ("4", "4 - Satisfied / Productive"),
        ("5", "5 - Highly Satisfied / Peak Study Day"),
    ]

    mood_score = forms.ChoiceField(
        choices=MOOD_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Current emotional state",
    )
    stress_score = forms.ChoiceField(
        choices=STRESS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Level of exam/preparation stress",
    )
    energy_level = forms.ChoiceField(
        choices=ENERGY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Physical and mental energy levels",
    )
    sleep_quality = forms.ChoiceField(
        choices=SLEEP_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Last night's sleep evaluation",
    )
    study_satisfaction = forms.ChoiceField(
        choices=STUDY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Academic progress satisfaction today",
    )

    class Meta:
        model = MoodLog
        fields = [
            "mood_score",
            "stress_score",
            "energy_level",
            "sleep_quality",
            "study_satisfaction",
        ]
