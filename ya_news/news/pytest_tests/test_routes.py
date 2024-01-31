from http import HTTPStatus

from django.urls import reverse

import pytest

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ]
)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_client, expected_status',
    [
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ]
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_comment_edit_and_delete(comment, user_client,
                                 expected_status, name):
    url = reverse(name, args=(comment.id,))
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonynous_user(client, comment, name):
    url = reverse(name, args=(comment.id,))
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
