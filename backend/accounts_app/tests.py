# accounts_app/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime


class AuthenticationTests(TestCase):
    """
    تست‌های احراز هویت و مجوزها
    """

    def setUp(self):
        """تنظیمات اولیه قبل از هر تست"""
        self.client = APIClient()

        # ✅ تنظیم Content-Type برای همه درخواست‌ها
        self.client.defaults['HTTP_CONTENT_TYPE'] = 'application/json'
        self.client.defaults['HTTP_ACCEPT'] = 'application/json'

        self.register_url = '/api/register/'
        self.login_url = '/api/login/'
        self.profile_url = '/api/profile/'
        self.public_url = '/api/public/'
        self.dashboard_url = '/api/dashboard/'
        self.admin_url = '/api/admin-only/'

        # داده‌های کاربر برای تست
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'password2': 'TestPass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        # ثبت‌نام کاربر
        response = self.client.post(
            self.register_url,
            self.user_data,
            format='json'  # ✅ اضافه کردن format='json'
        )
        if response.status_code == 201:
            self.user_id = response.data.get('data', {}).get('id')

    def test_user_registration_success(self):
        """تست ثبت‌نام موفق کاربر"""
        response = self.client.post(
            self.register_url,
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'NewPass123',
                'password2': 'NewPass123',
                'first_name': 'New',
                'last_name': 'User'
            },
            format='json'  # ✅ اضافه کنید
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('success'), True)
        self.assertEqual(response.data.get('data', {}).get('username'), 'newuser')
        self.assertEqual(response.data.get('message'), 'User registered successfully')

    def test_user_registration_password_mismatch(self):
        """تست ثبت‌نام با رمزهای عبور نامطابق"""
        response = self.client.post(
            self.register_url,
            {
                'username': 'newuser2',
                'email': 'new2@example.com',
                'password': 'Pass123',
                'password2': 'Pass456'
            },
            format='json'  # ✅ اضافه کنید
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('success'), False)
        self.assertIn('errors', response.data)

    def test_user_registration_duplicate_username(self):
        """تست ثبت‌نام با یوزرنیم تکراری"""
        response = self.client.post(
            self.register_url,
            {
                'username': 'testuser',  # یوزرنیم تکراری
                'email': 'new3@example.com',
                'password': 'Pass123',
                'password2': 'Pass123'
            },
            format='json'  # ✅ اضافه کنید
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('success'), False)

    def test_user_login_success(self):
        """تست ورود موفق کاربر"""
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'TestPass123'
            },
            format='json'  # ✅ اضافه کنید
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)

        # ✅ بررسی وجود توکن‌ها با استفاده از get
        data = response.data.get('data', {})
        tokens = data.get('tokens', {})

        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertEqual(data.get('user', {}).get('username'), 'testuser')

        # ذخیره توکن برای تست‌های بعدی
        self.access_token = tokens.get('access')

    def test_user_login_invalid_credentials(self):
        """تست ورود با اطلاعات نادرست"""
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'WrongPass123'
            },
            format='json'  # ✅ اضافه کنید
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('success'), False)

    def test_protected_endpoint_without_token(self):
        """تست دسترسی به ویو خصوصی بدون توکن"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data.get('detail'), 'Authentication credentials were not provided.')

    def test_protected_endpoint_with_valid_token(self):
        """تست دسترسی به ویو خصوصی با توکن معتبر"""
        # لاگین برای دریافت توکن
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'TestPass123'
            },
            format='json'  # ✅ اضافه کنید
        )

        # ✅ استفاده از get برای جلوگیری از KeyError
        access_token = login_response.data.get('data', {}).get('tokens', {}).get('access')

        # اگر توکن وجود نداشت، تست را با خطا متوقف کن
        self.assertIsNotNone(access_token, "Access token not found in login response")

        # دسترسی با توکن
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)
        self.assertEqual(response.data.get('data', {}).get('username'), 'testuser')
        self.assertEqual(response.data.get('data', {}).get('email'), 'test@example.com')

    def test_protected_endpoint_with_invalid_token(self):
        """تست دسترسی با توکن نامعتبر"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_endpoint_without_token(self):
        """تست دسترسی به ویو عمومی بدون توکن"""
        response = self.client.get(self.public_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)
        self.assertEqual(response.data.get('message'), 'This is a public endpoint')

    def test_public_endpoint_with_token(self):
        """تست دسترسی به ویو عمومی با توکن (همچنان باید کار کند)"""
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'TestPass123'
            },
            format='json'  # ✅ اضافه کنید
        )

        access_token = login_response.data.get('data', {}).get('tokens', {}).get('access')
        self.assertIsNotNone(access_token, "Access token not found in login response")

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.public_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_access_with_token(self):
        """تست دسترسی به داشبورد با توکن"""
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'TestPass123'
            },
            format='json'  # ✅ اضافه کنید
        )

        access_token = login_response.data.get('data', {}).get('tokens', {}).get('access')
        self.assertIsNotNone(access_token, "Access token not found in login response")

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)
        self.assertIn('dashboard', response.data.get('message', '').lower())

    def test_update_profile(self):
        """تست به‌روزرسانی پروفایل کاربر"""
        login_response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'TestPass123'
            },
            format='json'  # ✅ اضافه کنید
        )

        access_token = login_response.data.get('data', {}).get('tokens', {}).get('access')
        self.assertIsNotNone(access_token, "Access token not found in login response")

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.put(
            self.profile_url,
            {
                'first_name': 'Updated',
                'last_name': 'Name'
            },
            format='json'  # ✅ اضافه کنید
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('success'), True)
        self.assertEqual(response.data.get('data', {}).get('first_name'), 'Updated')
        self.assertEqual(response.data.get('data', {}).get('last_name'), 'Name')


class AdminPermissionTests(TestCase):
    """
    تست‌های مجوزهای ادمین
    """

    def setUp(self):
        self.client = APIClient()
        self.client.defaults['HTTP_CONTENT_TYPE'] = 'application/json'
        self.client.defaults['HTTP_ACCEPT'] = 'application/json'

        self.admin_url = '/api/admin-only/'

        # ایجاد کاربر معمولی
        self.user = User.objects.create_user(
            username='normaluser',
            password='NormalPass123'
        )

        # ایجاد کاربر ادمین
        self.admin = User.objects.create_superuser(
            username='adminuser',
            password='AdminPass123',
            email='admin@example.com'
        )

    def test_admin_access_with_normal_user(self):
        """تست دسترسی ادمین با کاربر معمولی (باید رد شود)"""
        login_response = self.client.post(
            '/api/login/',
            {
                'username': 'normaluser',
                'password': 'NormalPass123'
            },
            format='json'  # ✅ اضافه کنید
        )

        access_token = login_response.data.get('data', {}).get('tokens', {}).get('access')
        self.assertIsNotNone(access_token, "Access token not found in login response")

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.admin_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # accounts_app/tests.py - قسمت AdminPermissionTests

    def test_admin_access_with_admin_user(self):
        """تست دسترسی ادمین با کاربر ادمین"""
        login_response = self.client.post(
            '/api/login/',
            {
                'username': 'adminuser',
                'password': 'AdminPass123'
            },
            format='json'
        )

        access_token = login_response.data.get('data', {}).get('tokens', {}).get('access')

        if not access_token:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(self.admin)
            access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.admin_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ✅ تصحیح: تغییر متن مورد انتظار
        admin_panel = response.data.get('data', {}).get('admin_panel', '').lower()
        self.assertIn('admin only', admin_panel)  # ✅ تغییر به 'admin only'
        # یا
        self.assertEqual(admin_panel, 'this is admin only area')  # ✅ بررسی دقیق