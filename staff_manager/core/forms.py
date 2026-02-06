from django import forms
from .models import PerformanceTeam

class TeamForm(forms.ModelForm):
    class Meta:
        model = PerformanceTeam
        fields = ['name', 'start_date', 'end_date', 'description']
        widgets = {
            # 사용자가 달력에서 날짜와 시간을 쉽게 고를 수 있게 합니다.
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }