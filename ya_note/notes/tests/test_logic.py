from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteEditUpdate(TestCase):

    UPDATED_NOTE_TEXT = 'Измененный текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст',
            slug='testNote',
            author=cls.author
        )
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.login_url = reverse('users:login')
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Измененный текст',
            'slug': 'newNote',
        }

    def note_compare_to_form_data(self):
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def note_compare_to_db(self):
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)

    def test_anonymous_user_cannot_edit_notes(self):
        response = self.client.post(self.edit_url, data=self.form_data)
        redirect_url = f'{self.login_url}?next={self.edit_url}'
        self.assertRedirects(response, redirect_url)
        self.note_compare_to_db()

    def test_author_can_edit_notes(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note_compare_to_form_data()

    def test_user_cannot_edit_another_users_notes(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_compare_to_db()

    def test_anonymous_user_cannot_delete_notes(self):
        response = self.client.delete(self.delete_url)
        redirect_url = f'{self.login_url}?next={self.delete_url}'
        self.assertRedirects(response, redirect_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_delete_notes(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cannot_delete_another_users_notes(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)


class TestNoteAdd(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.add_url = reverse('notes:add')
        cls.login_url = reverse('users:login')
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': 'Заметка',
            'text': 'Текст',
            'slug': 'test',
        }

    def test_anonymous_user_cannot_create_notes(self):
        redirect_url = f'{self.login_url}?next={self.add_url}'
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_authorized_user_can_create_notes(self):
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_non_unique_slugs_cause_validation_error(self):
        note_obj = Note.objects.create(**self.form_data, author=self.author)
        response = self.author_client.post(self.add_url,
                                           data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(note_obj.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug_handling(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(note.title)[:100])
