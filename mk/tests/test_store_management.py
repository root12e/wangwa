from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from ..models.Department import Department
from ..models.store_management import Store, StoreInventory, StoreTransaction

User = get_user_model()

class StoreManagementTestCase(APITestCase):
    """店铺管理测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 创建部门
        self.department = Department.objects.create(
            name='测试部门',
            description='测试部门描述'
        )
        
        # 创建超级管理员用户
        self.super_admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='super_admin',
            status='approved'
        )
        
        # 创建部门部长用户
        self.department_manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass123',
            role='department_manager',
            department=self.department,
            status='approved'
        )
        
        # 创建店铺
        self.store = Store.objects.create(
            name='测试店铺',
            code='TEST001',
            address='测试地址',
            phone='12345678901',
            department=self.department,
            status='active'
        )
        
        # 创建店铺运营用户
        self.store_operator = User.objects.create_user(
            username='operator',
            email='operator@test.com',
            password='testpass123',
            role='store_operator',
            store=self.store,
            status='approved'
        )
        
        # 创建普通员工用户
        self.staff = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            role='staff',
            status='approved'
        )
    
    def get_token(self, user):
        """获取用户认证令牌"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_store_list_permissions(self):
        """测试店铺列表权限"""
        # 超级管理员可以查看所有店铺
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        response = self.client.get('/api/stores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 部门部长只能查看本部门店铺
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.department_manager)}')
        response = self.client.get('/api/stores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 只有1个店铺
        
        # 店铺运营只能查看自己的店铺
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.store_operator)}')
        response = self.client.get('/api/stores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 只有1个店铺
        
        # 普通员工可以查看店铺信息
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.staff)}')
        response = self.client.get('/api/stores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_store(self):
        """测试创建店铺"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        
        store_data = {
            'name': '新测试店铺',
            'code': 'TEST002',
            'address': '新测试地址',
            'phone': '12345678902',
            'department_id': str(self.department.id),
            'status': 'active',
            'description': '新测试店铺描述'
        }
        
        response = self.client.post('/api/stores/', store_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.count(), 2)
    
    def test_update_store(self):
        """测试更新店铺"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        
        update_data = {
            'name': '更新后的店铺名称',
            'description': '更新后的描述'
        }
        
        response = self.client.patch(f'/api/stores/{self.store.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证更新
        self.store.refresh_from_db()
        self.assertEqual(self.store.name, '更新后的店铺名称')
    
    def test_delete_store(self):
        """测试删除店铺"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        
        response = self.client.delete(f'/api/stores/{self.store.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Store.objects.count(), 0)
    
    def test_store_statistics(self):
        """测试店铺统计"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        
        response = self.client.get('/api/stores/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('total_stores', data)
        self.assertIn('active_stores', data)
        self.assertEqual(data['total_stores'], 1)
        self.assertEqual(data['active_stores'], 1)
    
    def test_change_store_status(self):
        """测试更改店铺状态"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        
        status_data = {'status': 'inactive'}
        response = self.client.post(f'/api/stores/{self.store.id}/change_status/', status_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证状态更改
        self.store.refresh_from_db()
        self.assertEqual(self.store.status, 'inactive')
    
    def test_my_stores(self):
        """测试获取我的店铺"""
        # 部门部长
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.department_manager)}')
        response = self.client.get('/api/stores/my_stores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # 店铺运营
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.store_operator)}')
        response = self.client.get('/api/stores/my_stores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
    
    def test_store_inventory_operations(self):
        """测试店铺库存操作"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        
        # 创建库存
        inventory_data = {
            'store_id': str(self.store.id),
            'product_name': '测试商品',
            'product_code': 'PROD001',
            'quantity': 100,
            'unit_price': '99.99',
            'min_stock': 10,
            'max_stock': 1000
        }
        
        response = self.client.post('/api/store-inventory/', inventory_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        inventory_id = response.data['id']
        
        # 调整库存
        adjustment_data = {
            'adjustment': 50,
            'reason': '补货入库'
        }
        
        response = self.client.post(f'/api/store-inventory/{inventory_id}/adjust_stock/', adjustment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证库存调整
        inventory = StoreInventory.objects.get(id=inventory_id)
        self.assertEqual(inventory.quantity, 150)
    
    def test_store_transactions(self):
        """测试店铺交易记录"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_token(self.super_admin)}')
        
        # 创建交易记录
        transaction_data = {
            'store_id': str(self.store.id),
            'transaction_type': 'sale',
            'amount': '299.99',
            'description': '测试销售交易'
        }
        
        response = self.client.post('/api/store-transactions/', transaction_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 获取每日汇总
        response = self.client.get('/api/store-transactions/daily_summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 获取月度报告
        response = self.client.get('/api/store-transactions/monthly_report/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
