from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime


from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Performance, Personnel, Team, Assignment, StandingTeam


# (메인, 스케줄 뷰는 기존 동일)
def main_hub(request): return render(request, 'core/main_hub.html')
def full_schedule(request):
    performances = Performance.objects.all().order_by('-date')
    return render(request, 'core/full_schedule.html', {'performances': performances})
def daily_schedule(request):
    date_str = request.GET.get('date')
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
    performances = Performance.objects.filter(date__date=target_date).order_by('date')
    return render(request, 'core/daily_schedule.html', {'performances': performances, 'target_date': target_date.strftime('%Y-%m-%d')})

# ==========================================
# [NEW] 인원 및 상설 팀 관리
# ==========================================
def personnel_list(request):
    personnel = Personnel.objects.all().order_by('standing_team', 'name')
    standing_teams = StandingTeam.objects.all()
    return render(request, 'core/personnel_list.html', {
        'personnel': personnel,
        'standing_teams': standing_teams
    })

# [상설 팀 생성]
@require_POST
def create_standing_team(request):
    name = request.POST.get('name')
    category = request.POST.get('category')
    if name: StandingTeam.objects.create(name=name, category=category)
    return redirect('core:personnel_list')

# [상설 팀 삭제]
def delete_standing_team(request, pk):
    get_object_or_404(StandingTeam, pk=pk).delete()
    return redirect('core:personnel_list')

# [인원 추가 (소속 팀 선택 가능)]
def personnel_add(request):
    standing_teams = StandingTeam.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('default_role')
        team_id = request.POST.get('standing_team')

        team = StandingTeam.objects.get(pk=team_id) if team_id else None
        Personnel.objects.create(name=name, default_role=role, standing_team=team)
        return redirect('core:personnel_list')
    return render(request, 'core/personnel_form.html', {'standing_teams': standing_teams, 'action': '추가'})

# [인원 수정]
def personnel_edit(request, pk):
    person = get_object_or_404(Personnel, pk=pk)
    standing_teams = StandingTeam.objects.all()
    if request.method == 'POST':
        person.name = request.POST.get('name')
        person.default_role = request.POST.get('default_role')
        team_id = request.POST.get('standing_team')
        person.standing_team = StandingTeam.objects.get(pk=team_id) if team_id else None
        person.save()
        return redirect('core:personnel_list')
    return render(request, 'core/personnel_form.html', {'person': person, 'standing_teams': standing_teams, 'action': '수정'})

def personnel_delete(request, pk):
    get_object_or_404(Personnel, pk=pk).delete()
    return redirect('core:personnel_list')

# ==========================================
# [공연 상세] 팀 불러오기 로직 적용
# ==========================================
def performance_detail(request, pk):
    perf = get_object_or_404(Performance, pk=pk)
    teams = perf.teams.all().prefetch_related('members')

    # 불러올 수 있는 상설 팀 목록 (이미 불러온 이름은 제외하거나 표시하면 좋지만 일단 다 보여줌)
    standing_teams = StandingTeam.objects.all()

    # 배정되지 않은 인원 (왼쪽 대기 명단)
    assigned_ids = Assignment.objects.filter(team__performance=perf, personnel__isnull=False).values_list('personnel_id', flat=True)
    available_personnel = Personnel.objects.exclude(id__in=assigned_ids).order_by('standing_team', 'name')

    return render(request, 'core/performance_detail.html', {
        'performance': perf,
        'teams': teams,
        'standing_teams': standing_teams,
        'available_personnel': available_personnel
    })

# [핵심] 상설 팀 불러오기 (Import)
@require_POST
def import_standing_team(request, perf_id):
    perf = get_object_or_404(Performance, pk=perf_id)
    standing_team_id = request.POST.get('standing_team_id')

    if standing_team_id:
        st_team = get_object_or_404(StandingTeam, pk=standing_team_id)

        # 1. 공연용 팀 생성 (이름 복사)
        new_team = Team.objects.create(
            performance=perf,
            name=st_team.name,
            category=st_team.category
        )

        # 2. 소속된 멤버들 자동 배정
        members = st_team.members.all()
        for mem in members:
            # 이미 다른 팀에 배정된 사람은 건너뛰기 (중복 방지)
            if Assignment.objects.filter(team__performance=perf, personnel=mem).exists():
                continue

            Assignment.objects.create(
                team=new_team,
                personnel=mem,
                display_name=mem.name,
                role_type='member' # 기본은 팀원으로
            )

    return redirect('core:performance_detail', pk=perf.pk)

# (기존 기능 유지)
def delete_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    pk = team.performance.pk
    team.delete()
    return redirect('core:performance_detail', pk=pk)

@require_POST
def add_members_to_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    person_ids = request.POST.getlist('person_ids')
    role_type = request.POST.get('role_type')

    if role_type == 'part_leader' and (team.members.filter(role_type='part_leader').exists() or len(person_ids) > 1):
        return redirect('core:performance_detail', pk=team.performance.pk)

    for pid in person_ids:
        person = get_object_or_404(Personnel, pk=pid)
        Assignment.objects.create(team=team, personnel=person, display_name=person.name, role_type=role_type)
    return redirect('core:performance_detail', pk=team.performance.pk)

def delete_assignment(request, assign_id):
    a = get_object_or_404(Assignment, pk=assign_id)
    pk = a.team.performance.pk
    a.delete()
    return redirect('core:performance_detail', pk=pk)

@require_POST
def update_status(request, pk):
    perf = get_object_or_404(Performance, pk=pk)
    action = request.POST.get('action')
    if action == 'approve': perf.status = 'approved'
    elif action == 'reject': perf.status = 'rejected'; perf.reason = request.POST.get('reason','')
    elif action == 'cancel': perf.status = 'canceled'; perf.reason = request.POST.get('reason','')
    perf.save()
    return redirect('core:performance_detail', pk=pk)

@require_POST
def delete_performance(request, pk):
    get_object_or_404(Performance, pk=pk).delete()
    return redirect('core:full_schedule')


@require_POST
def assign_personnel_bulk(request):
    team_id = request.POST.get('standing_team_id')
    person_ids = request.POST.getlist('person_ids') # 체크된 사람들 ID 목록

    if not person_ids:
        return redirect('core:personnel_list')

    if team_id == 'none':
        # '소속 해제'를 선택한 경우
        Personnel.objects.filter(id__in=person_ids).update(standing_team=None)
    elif team_id:
        # 특정 팀을 선택한 경우
        team = get_object_or_404(StandingTeam, pk=team_id)
        # 한 번에 업데이트 (Bulk Update)
        Personnel.objects.filter(id__in=person_ids).update(standing_team=team)

    return redirect('core:personnel_list')

# 에러 방지용 더미
@require_POST
def create_team(request, perf_id): return redirect('core:performance_detail', pk=perf_id)
@require_POST
def add_assignment_select(request, perf_id): return redirect('core:performance_detail', pk=perf_id)
@require_POST
def add_assignment_direct(request, perf_id): return redirect('core:performance_detail', pk=perf_id)
@require_POST
def update_assignment_role(request, assign_id): return redirect('core:performance_detail', pk=get_object_or_404(Assignment, pk=assign_id).team.performance.pk)