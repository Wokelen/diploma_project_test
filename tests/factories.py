import factory
from django.db import models
from django.utils import timezone
from pytest_factoryboy import register

from core.models import User
from goals.models import Board, BoardParticipant, GoalCategory, Goal, GoalComment


@register
class UserFactory(factory.django.DjangoModelFactory):

    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        return User.objects.create_user(*args, **kwargs)



class DateFactoryMixin(factory.django.DjangoModelFactory):

    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)


@register
class BoardFactory(DateFactoryMixin):

    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DateFactoryMixin):

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:

        model = BoardParticipant


@register
class GoalCategoryFactory(DateFactoryMixin):

    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)

    class Meta:

        model = GoalCategory


@register
class GoalFactory(DateFactoryMixin):

    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)

    class Meta:

        model: models.Model = Goal


@register
class GoalCommentFactory(DateFactoryMixin):

    text = factory.Faker('sentence')
    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)

    class Meta:

        model = GoalComment
