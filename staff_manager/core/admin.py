import csv
import io
from datetime import datetime
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from .models import Performance, Personnel

class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label="CSV 파일")

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    change_list_template = "admin/performance_change_list.html"
    list_display = ('title', 'date', 'status')

    def get_urls(self):
        return [
            path('import-schedule/', self.admin_site.admin_view(self.import_schedule), name='import_schedule'),
            path('import-personnel/', self.admin_site.admin_view(self.import_personnel), name='import_personnel'),
        ] + super().get_urls()

    # 1. 일정 업로드
    def import_schedule(self, request):
        if request.method == "POST":
            f = request.FILES["csv_file"]
            try: decoded = f.read().decode('utf-8-sig')
            except: f.seek(0); decoded = f.read().decode('cp949')

            reader = csv.DictReader(io.StringIO(decoded))
            count = 0
            for row in reader:
                if not row.get('Title'): continue
                try:
                    dt_str = row.get('Date', '').split('~')[0].strip()
                    dt = datetime.strptime(dt_str, "%Y-%m-%d")
                    Performance.objects.get_or_create(
                        title=row.get('Title'), date=dt,
                        defaults={'venue': row.get('Venue', row.get('Location','')), 'category': row.get('Category','')}
                    )
                    count += 1
                except: continue
            self.message_user(request, f"일정 {count}건 등록 완료")
            return redirect("..")
        return render(request, "admin/csv_form.html", {"form": CsvImportForm(), "title": "📅 전체일정 CSV 등록"})

    # 2. 인원 명부 업로드
    def import_personnel(self, request):
        if request.method == "POST":
            f = request.FILES["csv_file"]
            try: decoded = f.read().decode('utf-8-sig')
            except: f.seek(0); decoded = f.read().decode('cp949')

            reader = csv.reader(io.StringIO(decoded))
            count = 0
            for row in reader:
                if len(row) < 2: continue
                role = row[0].strip()
                name = row[1].strip()

                # 이름이 3번째 칸에 성이 따로 있는 경우 합치기 (예: 도현, 류 -> 류도현)
                if len(row) > 2 and row[2].strip():
                    name = row[2].strip() + name

                if name:
                    Personnel.objects.get_or_create(name=name, defaults={'default_role': role})
                    count += 1
            self.message_user(request, f"인원 {count}명 명부 등록 완료")
            return redirect("..")
        return render(request, "admin/csv_form.html", {"form": CsvImportForm(), "title": "👥 인원(팀-표) CSV 등록"})

admin.site.register(Personnel)