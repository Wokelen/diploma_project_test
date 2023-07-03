import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.fields import DateTimeField

from goals.models import BoardParticipant, Goal
from tests.goal_test.factories import CreateGoalRequest


@pytest.mark.django_db()
class TestCreateGoalView:
    url = reverse('goals:create_goal')

    def test_auth_required(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_board_if_not_participant(self, auth_client, board, goal_category, faker):
        data = CreateGoalRequest.build(category=goal_category.id)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'must be owner or writer in project'}

    def test_goal_create_on_board_if_reader(self, auth_client, goal_category, board_participant, faker):

        board_participant.role = BoardParticipant.Role.reader
        board_participant.save(update_fields=['role'])

        data = CreateGoalRequest.build(category=goal_category.id)
        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Must e owner or writer in project'}

    @pytest.mark.parametrize('role', [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                             ids=['owner', 'writer'])
    def test_goal_create_on_board_for_owner_or_writer(self, auth_client, goal_category, board_participant, faker, role):

        board_participant.role = role
        board_participant.save(update_fields=['role'])

        data = CreateGoalRequest.build(category=goal_category.id)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        new_goal = Goal.objects.get()
        assert response.json() == _serializer_response(new_goal)

    @pytest.mark.usefixtures('board_participants')
    def test_goal_create_for_not_existing_category(self, auth_client):
        data = CreateGoalRequest.build(category=1)
        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Invalid pk "1" - object does not exist.']}

    @pytest.mark.usefixtures('board_participants')
    def test_goal_create_on_is_deleted_category(self, auth_client, goal_category):

        goal_category.is_deleted = True
        goal_category.save(update_fields=['is_deleted'])

        data = CreateGoalRequest.build(category=goal_category.id)
        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Category not found']}


def _serializer_response(goal: Goal, **kwargs) -> dict:

    data = {'id': goal.id,
            'category': goal.category_id,
            'created': DateTimeField().to_representation(goal.created),
            'updated': DateTimeField().to_representation(goal.updated),
            'title': goal.title,
            'description': goal.description,
            'status': goal.status,
            'priority': goal.priority,
            'due_date': DateTimeField().to_representation(goal.due_date),
            }
    return data | kwargs

