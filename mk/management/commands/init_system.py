from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mk.models import Department, Store
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = '初始化系统基础数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化系统数据...')
        
        try:
            with transaction.atomic():
                # 创建默认部门
                default_dept, created = Department.objects.get_or_create(
                    name='总部',
                    defaults={
                        'description': '公司总部管理部门'
                    }
                )
                if created:
                    self.stdout.write(f'✓ 创建部门: {default_dept.name}')
                else:
                    self.stdout.write(f'✓ 部门已存在: {default_dept.name}')
                
                # 创建默认店铺
                default_store, created = Store.objects.get_or_create(
                    name='总部店铺',
                    defaults={
                        'address': '公司总部地址',
                        'phone': '400-000-0000',
                        'department': default_dept
                    }
                )
                if created:
                    self.stdout.write(f'✓ 创建店铺: {default_store.name}')
                else:
                    self.stdout.write(f'✓ 店铺已存在: {default_store.name}')
                
                # 创建超级管理员
                if not User.objects.filter(role='super_admin').exists():
                    super_admin = User.objects.create_user(
                        username='admin',
                        email='admin@wwkc.com',
                        phone='13800000000',
                        password='admin123456',
                        role='super_admin',
                        is_staff=True,
                        is_superuser=True,
                        is_email_verified=True
                    )
                    self.stdout.write(f'✓ 创建超级管理员: {super_admin.username}')
                else:
                    self.stdout.write('✓ 超级管理员已存在')
                
                # 创建部门部长示例
                if not User.objects.filter(role='department_manager').exists():
                    dept_manager = User.objects.create_user(
                        username='dept_manager',
                        email='dept_manager@wwkc.com',
                        phone='13800000001',
                        password='dept123456',
                        role='department_manager',
                        department=default_dept,
                        is_staff=True,
                        is_email_verified=True
                    )
                    self.stdout.write(f'✓ 创建部门部长: {dept_manager.username}')
                else:
                    self.stdout.write('✓ 部门部长已存在')
                
                # 创建店铺运营示例
                if not User.objects.filter(role='store_operator').exists():
                    store_operator = User.objects.create_user(
                        username='store_operator',
                        email='store_operator@wwkc.com',
                        phone='13800000002',
                        password='store123456',
                        role='store_operator',
                        department=default_dept,
                        store=default_store,
                        is_email_verified=True
                    )
                    self.stdout.write(f'✓ 创建店铺运营: {store_operator.username}')
                else:
                    self.stdout.write('✓ 店铺运营已存在')
                
                # 创建普通员工示例
                if not User.objects.filter(role='staff').exists():
                    staff = User.objects.create_user(
                        username='staff',
                        email='staff@wwkc.com',
                        phone='13800000003',
                        password='staff123456',
                        role='staff',
                        department=default_dept,
                        store=default_store,
                        is_email_verified=True
                    )
                    self.stdout.write(f'✓ 创建普通员工: {staff.username}')
                else:
                    self.stdout.write('✓ 普通员工已存在')
                
                self.stdout.write(
                    self.style.SUCCESS('系统初始化完成！\n\n'
                                     '默认账户信息：\n'
                                     '超级管理员: admin / admin123456\n'
                                     '部门部长: dept_manager / dept123456\n'
                                     '店铺运营: store_operator / store123456\n'
                                     '普通员工: staff / staff123456')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'初始化失败: {str(e)}')
            )
            raise
