from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post

class TestView(TestCase):
    def setUp(self):
        self.client=Client()
        self.user_trump=User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

    def test_post_list(self):
        # 1.1 포스트 목록 페이지 가져오기
        response=self.client.get('/blog/')
        #1.2 정상적으로 페이지 로드
        self.assertEqual(response.status_code, 200)
        #1.3 페이지 타이틀은 'Blog'
        soup=BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        self.navbar_test(soup)

        #2.1 메인 영역에 게시물이 하나도 없으면
        self.assertEqual(Post.objects.count(), 0)
        #2.2 '아직 게시물이 없습니다' 출력
        main_area=soup.find('div', id="main-area")
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        #3.1 게시물이 2개 있으면
        post_001=Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
            author=self.user_trump
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='콩콩콩콩.',
            author=self.user_obama
        )
        self.assertEqual(Post.objects.count(), 2)
        #3.2 포스트 목록 페이지 새로고침 시
        response=self.client.get('/blog/')
        soup=BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        #3.3 메인 영역에 포스트 2개 타이틀 존재
        main_area = soup.find('div', id="main-area")
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        #3.4 '아직 게시물이 없습니다'라는 문구는 안보임
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

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