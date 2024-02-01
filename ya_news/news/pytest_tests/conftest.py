import pytest

from django.test import Client
from django.utils import timezone
from django.conf import settings

from news.models import News, Comment

from datetime import datetime, timedelta


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def multiple_news():
    today = datetime.today()
    news_list = [
        News(
            title=f'Заголовок {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def news_multiple_comments(news, author):
    for index in range(10):
        now = timezone.now()
        comment = Comment.objects.create(
            author=author,
            news=news,
            text=f'Текст {index}'
        )
        comment.created = now - timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def news_pk_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_form_data():
    return {'text': 'Новый текст комментария'}
