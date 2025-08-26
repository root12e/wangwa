from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mk.models import Department, Store
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = '初始化部门管理测试数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化部门管理测试数据...')
        
        try:
            with transaction.atomic():
                # 创建多个部门
                departments_data = [
                    {
                        'name': '技术部',
                        'description': '负责产品研发和技术支持'
                    },
                    {
                        'name': '销售部',
                        'description': '负责产品销售和市场拓展'
                    },
                    {
                        'name': '运营部',
                        'description': '负责日常运营和客户服务'
                    },
                    {
                        'name': '财务部',
                        'description': '负责财务管理和资金控制'
                    },
                    {
                        'name': '人事部',
                        'description': '负责人力资源管理'
                    }
                ]
                
                created_departments = []
                for dept_data in departments_data:
                    dept, created = Department.objects.get_or_create(
                        name=dept_data['name'],
                        defaults=dept_data
                    )
                    created_departments.append(dept)
                    if created:
                        self.stdout.write(f'✓ 创建部门: {dept.name}')
                    else:
                        self.stdout.write(f'✓ 部门已存在: {dept.name}')
                
                # 为每个部门创建店铺
                for dept in created_departments:
                    store_name = f'{dept.name}店铺'
                    store, created = Store.objects.get_or_create(
                        name=store_name,
                        defaults={
                            'address': f'{dept.name}办公地址',
                            'phone': f'400-{dept.id.hex[:4]}-{dept.id.hex[4:8]}',
                            'department': dept
                        }
                    )
                    if created:
                        self.stdout.write(f'✓ 创建店铺: {store.name}')
                    else:
                        self.stdout.write(f'✓ 店铺已存在: {store.name}')
                
                # 为每个部门创建部门部长
                for dept in created_departments:
                    manager_username = f'{dept.name.lower()}_manager'
                    if not User.objects.filter(username=manager_username).exists():
                        manager = User.objects.create_user(
                            username=manager_username,
                            email=f'{manager_username}@wwkc.com',
                            phone=f'138{dept.id.hex[:8]}',
                            password=f'{dept.name.lower()}123456',
                            role='department_manager',
                            department=dept,
                            is_staff=True,
                            is_email_verified=True
                        )
                        self.stdout.write(f'✓ 创建部门部长: {manager.username} (部门: {dept.name})')
                    else:
                        self.stdout.write(f'✓ 部门部长已存在: {manager_username}')
                
                # 为每个部门创建一些员工
                for dept in created_departments:
                    store = Store.objects.filter(department=dept).first()
                    if store:
                        # 创建店铺运营
                        operator_username = f'{dept.name.lower()}_operator'
                        if not User.objects.filter(username=operator_username).exists():
                            operator = User.objects.create_user(
                                username=operator_username,
                                email=f'{operator_username}@wwkc.com',
                                phone=f'139{dept.id.hex[:8]}',
                                password=f'{dept.name.lower()}123456',
                                role='store_operator',
                                department=dept,
                                store=store,
                                is_email_verified=True
                            )
                            self.stdout.write(f'✓ 创建店铺运营: {operator.username} (部门: {dept.name})')
                        
                        # 创建普通员工
                        for i in range(1, 4):  # 每个部门创建3个普通员工
                            staff_username = f'{dept.name.lower()}_staff_{i}'
                            if not User.objects.filter(username=staff_username).exists():
                                staff = User.objects.create_user(
                                    username=staff_username,
                                    email=f'{staff_username}@wwkc.com',
                                    phone=f'137{dept.id.hex[:8]}{i:02d}',
                                    password=f'{dept.name.lower()}123456',
                                    role='staff',
                                    department=dept,
                                    store=store,
                                    is_email_verified=True
                                )
                                self.stdout.write(f'✓ 创建普通员工: {staff.username} (部门: {dept.name})')
                
                self.stdout.write(
                    self.style.SUCCESS('\n部门管理测试数据初始化完成！\n\n'
                                     '已创建以下部门：\n')
                )
                
                for dept in created_departments:
                    user_count = User.objects.filter(department=dept, is_active=True).count()
                    store_count = Store.objects.filter(department=dept).count()
                    self.stdout.write(f'  • {dept.name}: {user_count} 个用户, {store_count} 个店铺')
                
                self.stdout.write(
                    self.style.SUCCESS('\n测试账户信息：\n'
                                     '技术部部长: jishubu_manager / jishubu123456\n'
                                     '销售部部长: xiaoshoubu_manager / xiaoshoubu123456\n'
                                     '运营部部长: yunyingbu_manager / yunyingbu123456\n'
                                     '财务部部长: caiwubu_manager / caiwubu123456\n'
                                     '人事部部长: renshibu_manager / renshibu123456')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'初始化失败: {str(e)}')
            )
            raise
