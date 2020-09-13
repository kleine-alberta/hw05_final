import shutil
import tempfile
import os
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.cache import cache

from posts.models import Group, Post, User, Comment, Follow

from django.test import override_settings

temp = 'test'


class TestSuits(TestCase):
    def setUp(self):
        self.client = Client()
        self.unlogged_client = Client()
        self.user = User.objects.create_user(username='john')
        self.client.force_login(self.user)
        self.group = Group.objects.create(title='group_1',
                                          slug='group_1')
        self.post = Post.objects.create(
            text='тестовая',
            author=self.user,
            group=self.group,
        )

    def tearDown(self):
        try:
            shutil.rmtree(temp)
        except OSError:
            pass

    def check_response(self, new_post):
        urls = [
            reverse('post', args=[new_post.author.username, new_post.id]),
            reverse('index'),
            reverse('profile', args=[new_post.author.username]),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, new_post.text, status_code=200)
            self.assertContains(response, new_post.author, status_code=200)
            self.assertContains(response, new_post.group.id, status_code=200)

    def test_profile_check(self):
        res = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(res.status_code, 200)

    def test_nonautorized_user_cant_make_post(self):
        response = self.unlogged_client.post(reverse('new_post'))
        login_url = reverse('login')
        new_post_url = reverse('new_post')
        url_to_check = f'{login_url}?next={new_post_url}'
        self.assertRedirects(response, url_to_check)
        self.assertFalse(Post.objects.filter(author=self.user,
                                             text='text',
                                             group=self.group).exists())

    def test_autorized_user_can_make_post(self):
        response = self.client.post(reverse('new_post'),
                                    data={'text': 'какой-то текст',
                                          'group': self.group.id})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(author=self.user,
                                            text='какой-то текст',
                                            group=self.group.id).exists())

    def test_new_post_appears_everywhere(self):
        cache.clear()
        new_post = Post.objects.create(
            text='тестовая запись',
            author=self.user,
            group=self.group,
        )
        self.check_response(new_post)

    def test_check_edited_post_is_everyweher(self):
        cache.clear()
        response = self.client.post(reverse('post_edit',
                                            args=[self.post.author.username,
                                                  self.post.id]),
                                    data={'text': 'какой-то текст',
                                          'group': self.group.id},
                                    follow=True)
        edit_post = response.context['post']
        self.check_response(edit_post)

    def test_404_response(self):
        resp = self.client.get('/profile/none/')
        self.assertEqual(resp.status_code, 404)

    @override_settings(MEDIA_ROOT=(temp + '/media'))
    def test_tag_img_exists_in_post_page(self):
        cache.clear()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
            )
        img = SimpleUploadedFile('small.gif', small_gif,
                                 content_type='image/gif')
        data = {
                'text': 'post with image',
                'group': self.group.id,
                'image': img,
                }
        post = self.client.post(reverse('new_post'), data=data, follow=True)
        urls = [
                reverse('index'),
                reverse('profile', args=[self.post.author.username]),
                reverse('post', args=[self.post.author.username,
                                      self.post.id + 1]),
                reverse('group', args=[self.group.slug]),
                ]
        for url in urls:
            post = self.client.post(url)
            self.assertIn('<img'.encode(), post.content)

    @override_settings(MEDIA_ROOT=(temp + '/media'))
    def test_non_graffic_format_load(self):
        small_gif = (
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        img = SimpleUploadedFile('small.doc', small_gif,
                                 content_type='doc')
        resp = self.client.post(reverse('new_post'),
                                {'author': self.user,
                                 'text': 'post with no image',
                                 'group': self.group.id,
                                 'image': img})
        form = resp.context['form']
        self.assertFalse(form.is_valid())
        self.assertFormError(resp, 'form', 'image', form.errors['image'])
        self.assertFormError(resp, 'form', 'image',
                             'Загрузите правильное изображение. '
                             'Файл, который вы загрузили, '
                             'поврежден или не является изображением.')

    def test_cache_work(self):
        self.client.get(reverse('index'))
        self.client.post(reverse('new_post'),
                         data={'text': 'проверка кэша',
                               'group': self.group.id})
        post_1 = self.client.get(reverse('index'))
        self.assertNotIn("проверка кэша".encode(), post_1.content)

    def test_authorized_user_can_make_subscribes(self):
        author = get_user_model().objects.create_user(username='TestUser')
        self.client.post(reverse('profile_follow', args=[author]))
        resp = self.client.post(reverse('profile', args=[author]))
        response = self.client.post(reverse('profile', args=[self.user]))
        follower = response.context['followers']
        self.assertEqual(response.status_code, 200)
        self.assertIn("Отписаться".encode(), resp.content)
        self.assertEqual(follower, 1)

    def test_autorized_user_can_cancel_subscibes(self):
        author = get_user_model().objects.create_user(username='TestUser')
        self.client.post(reverse('profile_follow', args=[author]))
        self.client.post(reverse('profile_unfollow',
                                 args=[author]))
        resp = self.client.post(reverse('profile', args=[author]))
        response = self.client.post(reverse('profile', args=[self.user]))
        followers = response.context['followers']
        self.assertEqual(response.status_code, 200)
        self.assertIn("Подписаться".encode(), resp.content)
        self.assertEqual(followers, 0)

    def test_autorized_user_can_make_comments(self):
        response = self.client.post(reverse('add_comment',
                                    args=[self.user, self.post.id]),
                                    data={'text': 'коммент'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(author=self.user,
                                               text='коммент'))

    def test_new_post_appear_at_followers(self):
        author = get_user_model().objects.create_user(username='TestUser')
        follow = Follow.objects.create(user=self.user, author=author)
        new_follow_post = Post.objects.create(
            text='новая запись',
            author=follow.author,
            group=self.group,
        )
        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, new_follow_post.text, status_code=200)

    def test_new_post_doesnt_appear_at_non_followers(self):
        author = get_user_model().objects.create_user(username='TestUser')
        Post.objects.create(
            text=("moeow-meow"),
            author=author,
            group=self.group
        )
        response = self.client.get(reverse("follow_index"))
        self.assertNotContains(response, "moeow-meow")
