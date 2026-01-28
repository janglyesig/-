# core/admin.py
import csv
import io
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django import forms
from .models import Personnel, Team

# CSV 업로드용 폼
class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="CSV 파일 선택")

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('position', 'name')
    change_list_template = "admin/personnel_change_list.html"  # 커스텀 템플릿 지정

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            # 파일 형식 확인
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "CSV 파일만 업로드 가능합니다.")
                return redirect("..")

            # CSV 읽기 및 데이터 저장
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            # 첫 줄(헤더) 건너뛰기 여부는 CSV 파일 상태에 따라 결정 (여기선 첫줄이 '직급,이름' 헤더라고 가정하고 건너뜀)
            next(io_string, None)

            for row in csv.reader(io_string):
                # row[0]: 직급, row[1]: 이름
                if len(row) >= 2:
                    Personnel.objects.create(
                        position=row[0],
                        name=row[1]
                    )

            self.message_user(request, "CSV 명단이 성공적으로 업로드되었습니다.")
            return redirect("..")

        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    filter_horizontal = ('members',) # 다대다 필드 보기 좋게 설정
