from django.core.management.base import BaseCommand
from django.db import transaction
from mk.models.Department import Department
from mk.models.store_management import Store
from mk.models.User import User

class Command(BaseCommand):
    help = '初始化店铺示例数据'
    
    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('开始创建店铺示例数据...')
            
            # 检查是否已有部门
            if not Department.objects.exists():
                self.stdout.write('请先创建部门数据')
                return
            
            # 检查是否已有店铺
            if Store.objects.exists():
                self.stdout.write('店铺数据已存在，跳过初始化')
                return
            
            # 获取第一个部门作为默认部门
            default_department = Department.objects.first()
            
            # 创建示例店铺
            stores_data = [
                {
                    'name': '北京朝阳店',
                    'code': 'BJ001',
                    'address': '北京市朝阳区建国门外大街1号',
                    'phone': '010-12345678',
                    'email': 'bj001@example.com',
                    'department': default_department,
                    'status': 'active',
                    'description': '北京朝阳区主要店铺',
                    'business_hours': '09:00-22:00'
                },
                {
                    'name': '上海浦东店',
                    'code': 'SH001',
                    'address': '上海市浦东新区陆家嘴环路1000号',
                    'phone': '021-87654321',
                    'email': 'sh001@example.com',
                    'department': default_department,
                    'status': 'active',
                    'description': '上海浦东新区主要店铺',
                    'business_hours': '09:00-22:00'
                },
                {
                    'name': '广州天河店',
                    'code': 'GZ001',
                    'address': '广州市天河区天河路385号',
                    'phone': '020-11223344',
                    'email': 'gz001@example.com',
                    'department': default_department,
                    'status': 'active',
                    'description': '广州天河区主要店铺',
                    'business_hours': '09:00-22:00'
                }
            ]
            
            created_stores = []
            for store_data in stores_data:
                store = Store.objects.create(**store_data)
                created_stores.append(store)
                self.stdout.write(f'创建店铺: {store.name} ({store.code})')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功创建 {len(created_stores)} 个店铺'
                )
            )
