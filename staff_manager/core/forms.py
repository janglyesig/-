# core/forms.py
from django import forms
from .models import Assignment

class CSVUploadForm(forms.Form):
    file = forms.FileField(label="CSV 파일 선택")

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['person', 'task', 'detail']
        widgets = {
            'person': forms.Select(attrs={'class': 'form-select'}),
            'task': forms.Select(attrs={'class': 'form-select'}),
            'detail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '공연명 또는 메모 입력'}),
        }