from django.urls import reverse
from django.conf import settings

import pytest

from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.usefixtures('multiple_news')
def test_home_page_news_count_and_order(client):
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page_comment_order(client, news_multiple_comments):
    url = reverse('news:detail', args=(news_multiple_comments.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    comment_set = news_obj.comment_set.all()
    all_dates = [comment.created for comment in comment_set]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page_no_comment_form_for_anonymous_user(
    client, news_pk_for_args
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_detail_page_authorized_user_has_form(
    author_client, news_pk_for_args
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
