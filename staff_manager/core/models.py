from django.db import models

# [1] 상설 팀 (인원 관리 탭에서 만드는 고정 팀) - NEW!
class StandingTeam(models.Model):
    CATEGORY_CHOICES = [('general', '일반팀'), ('prep', '준비팀'), ('religion', '종교팀')]
    name = models.CharField(max_length=100, verbose_name="팀명")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')

    def __str__(self): return self.name

# [2] 인원 명부 (상설 팀 소속 정보 추가)
class Personnel(models.Model):
    name = models.CharField(max_length=100)
    default_role = models.CharField(max_length=100, blank=True)
    # 어느 상설 팀 소속인지 연결
    standing_team = models.ForeignKey(StandingTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='members', verbose_name="소속 팀")

    def __str__(self): return f"{self.name} ({self.default_role})"

# [3] 공연 일정
class Performance(models.Model):
    STATUS_CHOICES = [('pending','승인대기'), ('approved','승인완료'), ('canceled','취소'), ('rejected','반려')]
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    venue = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-date']

# [4] 공연용 팀 (공연 때마다 생성되는 실행 팀)
class Team(models.Model):
    # 상설 팀 정보를 복사해오지만, 공연마다 수정될 수 있으므로 별도 저장
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20)

    def __str__(self): return f"[{self.performance.title}] {self.name}"

# [5] 배정 (인원 -> 공연용 팀)
class Assignment(models.Model):
    ROLE_CHOICES = [('part_leader', '👑 파트장'), ('team_leader', '🧢 팀장'), ('member', '🙂 팀원')]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    personnel = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True, blank=True)
    display_name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')