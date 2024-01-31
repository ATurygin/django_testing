from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from http import HTTPStatus


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_pk_for_args,
                                            comment_form_data):
    url = reverse('news:detail', args=news_pk_for_args)
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news,
                                 comment_form_data, author):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment, news_pk_for_args):
    url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=news_pk_for_args)
    comments_url = f'{news_url}#comments'
    response = author_client.post(url)
    assertRedirects(response, comments_url)
    assert Comment.objects.count() == 0


def test_user_cannot_delete_comment_of_another_user(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment,
                                 news_pk_for_args,
                                 comment_form_data):
    url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=news_pk_for_args)
    comments_url = f'{news_url}#comments'
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, comments_url)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


def test_user_cannot_edit_comment_of_another_user(reader_client, comment,
                                                  comment_form_data):
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
