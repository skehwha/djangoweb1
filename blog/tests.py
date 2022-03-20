from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

class TestView(TestCase):
    def setUp(self):
        self.client=Client()
        self.user_trump=User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.category_programming=Category.objects.create(name='programming', slug='programming')
        self.user_obama.is_staff=True
        self.user_obama.save()
        self.category_sports=Category.objects.create(name='sports', slug='sports')

        self.tag_python_kr = Tag.objects.create(name="파이썬 공부", slug="파이썬-공부")
        self.tag_python = Tag.objects.create(name="python", slug="python")
        self.tag_hello = Tag.objects.create(name="hello", slug="hello")

        self.post_001=Post.objects.create(
            title='첫번째 포스트',
            content='Hello, World!',
            category=self.category_programming,
            author=self.user_trump
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두번째 포스트',
            content='V5 화이팅',
            category=self.category_sports,
            author=self.user_obama
        )

        self.post_003 = Post.objects.create(
            title='세번째 포스트',
            content='카테고리 없음',
            author=self.user_obama
        )
        self.post_003.tags.add(self.tag_python_kr)
        self.post_003.tags.add(self.tag_python)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup=BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area=soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def category_card_test(self, soup):
        categories_card=soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_sports.name} ({self.category_sports.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def test_post_list(self):
        #포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response=self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup=BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area=soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card=main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kr.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kr.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kr.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        #포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response=self.client.get('/blog/')
        soup=BeautifulSoup(response.content, 'html.parser')
        main_area=soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):

        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response=self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup=BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        #main_area=soup.find('div', id='main-area')
        post_area=soup.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        self.assertIn(self.user_trump.username.upper(), post_area.text)

        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kr.name, post_area.text)

    def navbar_test(self, soup):
        # 1.1 네비게이션바가 있음
        navbar = soup.nav
        # 1.2 Blog, About Me 라는 문구가 네비게이션 바에 있음
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text="Do It Django")
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text="Home")
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text="Blog")
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text="About Me")
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_category_page(self):
        #고유 url 부여, 상태 200 확인
        response=self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        #파싱
        soup=BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
        #카테고리 뱃지 나타나는지 확인
        self.assertIn(self.category_programming.name, soup.h1.text)
        #메인영역에 카테고리 이름이 있는지 확인, 이 카테고리에 해당하는 포스트만 노출, 그 외는 안보임
        main_area=soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        #비로그인시 status code != 200
        response=self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        #staff 아닌 계정
        self.client.login(username='trump', password='somepassword')
        response=self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        #staff 계정
        self.client.login(username='obama', password='somepassword')

        response=self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup=BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area=soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': 'Post Form 만들기',
            }
        )
        last_post=Post.objects.last()
        self.assertEqual(last_post.title, 'Post Form 만들기')
        self.assertEqual(last_post.author.username, 'obama')