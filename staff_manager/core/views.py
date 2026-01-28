# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Personnel, Team

def index(request):
    if request.method == "POST":
        team_name = request.POST.get('team_name')
        selected_ids = request.POST.getlist('selected_people')

        if team_name and selected_ids:
            new_team = Team.objects.create(name=team_name)
            members = Personnel.objects.filter(id__in=selected_ids)
            new_team.members.add(*members)
            return redirect('index')

    # [수정된 부분]
    # teams__isnull=True : 팀에 소속되지 않은(Null) 사람만 가져오기
    people = Personnel.objects.filter(teams__isnull=True).order_by('position', 'name')

    # 팀 목록은 최신순으로
    teams = Team.objects.all().order_by('-created_at')

    return render(request, 'core/index.html', {
        'people': people,
        'teams': teams
    })

# [추가된 함수] 팀 삭제하기 (삭제하면 인원들은 다시 목록으로 복귀됨)
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    team.delete()
    return redirect('index')
# [추가된 함수] 팀 수정하기
def edit_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == "POST":
        # 1. 팀 이름 수정
        team_name = request.POST.get('team_name')
        if team_name:
            team.name = team_name
            team.save()

        # 2. 멤버 수정 (체크된 사람만 이 팀의 멤버가 됨)
        selected_ids = request.POST.getlist('selected_people')

        # 선택된 인원들을 조회
        new_members = Personnel.objects.filter(id__in=selected_ids)

        # 팀 멤버를 '새로 선택된 명단'으로 덮어쓰기 (.set() 사용)
        # 선택 해제된 사람은 자동으로 팀에서 빠져나가 대기 명단으로 돌아갑니다.
        team.members.set(new_members)

        return redirect('index')

    # [화면 보여주기]
    # 수정 화면에는 '이미 이 팀인 사람(Q(teams=team))' + '팀이 없는 사람(Q(teams__isnull=True))'이 모두 나와야 함
    available_people = Personnel.objects.filter(
        Q(teams__isnull=True) | Q(teams=team)
    ).distinct().order_by('position', 'name')

    return render(request, 'core/edit_team.html', {
        'team': team,
        'people': available_people,
    })