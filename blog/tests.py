from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category

class TestView(TestCase):
    def setUp(self):
        self.client=Client()
        self.user_trump=User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.category_programming=Category.objects.create(name='programming', slug='programming')
        self.category_sports=Category.objects.create(name='sports', slug='sports') #여기까지함
        self.post_001=Post.objects.create(
            title='첫번째 포스트',
            content='Hello, World!',
            category=self.category_programming,
            author=self.user_trump
        )
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

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)

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
        # 1.1 포스트 1개 생성
        post_001=Post.objects.create(
            title='첫 번째 포스트입니다',
            content='Hello World',
            author=self.user_trump,
        )
        # 1.2 포스트의 url은 '/blog/1/'
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        # 2 첫번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근시 정상작동(status code 200)
        response=self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup=BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        # 2.3 첫 번째 포스트 제목이 웹브라우저 탭 타이틀에 있음
        self.assertIn(post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있음
        main_area=soup.find('div', id='main-area')
        post_area=soup.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)
        # 2.5 첫 번째 포스트의 작성자가 포스트 영역에 있음
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        # 2.6 첫 번째 포스트의 내용이 포스트 영역에 있음
        self.assertIn(post_001.content, post_area.text)

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

