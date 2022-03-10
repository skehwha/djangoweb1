from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

class TestView(TestCase):
    def setUp(self):
        self.client=Client()

    def test_post_list(self):
        # 1.1 포스트 목록 페이지 가져오기
        response=self.client.get('/blog/')
        #1.2 정상적으로 페이지 로드
        self.assertEqual(response.status_code, 200)
        #1.3 페이지 타이틀은 'Blog'
        soup=BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        #1.4 네비게이션바가 있음
        navbar=soup.nav
        #1.5 Blog, About Me 라는 문구가 네비게이션 바에 있음
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        #2.1 메인 영역에 게시물이 하나도 없으면
        self.assertEqual(Post.objects.count(), 0)
        #2.2 '아직 게시물이 없습니다' 출력
        main_area=soup.find('div', id="main-area")
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        #3.1 게시물이 2개 있으면
        post_001=Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='콩콩콩콩.',
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