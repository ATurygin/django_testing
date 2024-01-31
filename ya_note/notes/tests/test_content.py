from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Тестовый заголовок',
            text='Текст',
            slug='testnote',
            author=cls.author
        )

    def test_add_edit_pages_have_form(self):
        self.client.force_login(self.author)
        names = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in names:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)

    def test_delete_and_detail_pages(self):
        names = (
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for name, args in names:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('note', response.context)
                self.assertEqual(response.context['note'].id, self.note.id)


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.first_author = User.objects.create(username='Автор 1')
        cls.second_author = User.objects.create(username='Автор 2')
        cls.first_author_note = Note.objects.create(
            title='Заметка первого автора',
            text='Текст.',
            slug='first_author_note',
            author=cls.first_author
        )
        cls.second_author_note = Note.objects.create(
            title='Заметка второго автора',
            text='Текст.',
            slug='second_author_note',
            author=cls.second_author
        )

    def test_list_page(self):
        name = 'notes:list'
        url = reverse(name)
        self.client.force_login(self.first_author)
        response = self.client.get(url)
        self.assertIn('object_list', response.context)
        self.assertNotIn(self.second_author_note,
                         response.context['object_list'])
        note_obj = response.context['object_list'][0]
        self.assertEqual(note_obj, self.first_author_note)
