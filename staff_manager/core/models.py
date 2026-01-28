# core/models.py
from django.db import models

class Personnel(models.Model):
    position = models.CharField(max_length=50, verbose_name="직급")
    name = models.CharField(max_length=100, verbose_name="이름")

    def __str__(self):
        return f"[{self.position}] {self.name}"

    class Meta:
        verbose_name = "인원"
        verbose_name_plural = "인원 명단"

class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="팀명")
    # 팀원은 여러 명일 수 있고, 한 명이 여러 팀에 속할 수도 있다면 ManyToManyField 사용
    members = models.ManyToManyField(Personnel, related_name='teams', verbose_name="팀원")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "팀"
        verbose_name_plural = "팀 목록"