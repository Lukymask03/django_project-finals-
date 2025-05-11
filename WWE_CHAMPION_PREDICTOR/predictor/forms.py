from django import forms
from datetime import date

class PredictionForm(forms.Form):
    wrestler_name = forms.CharField(max_length=100, label='Wrestler Name')
    
    championship_choices = [
        ("wwe championship", "WWE Championship"),
        ("wwe us championship", "WWE US Championship"),
        ("wwe women's championship", "WWE Women's Championship"),
        ("wwe raw women's championship", "WWE Raw Women's Championship"),
        ("wwe smackdown women's championship", "WWE SmackDown Women's Championship"),
    ]
    
    championship = forms.ChoiceField(choices=championship_choices, label='Championship')
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1980, date.today().year + 1)), label='Start Date')
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1980, date.today().year + 1)), label='End Date')