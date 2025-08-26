from rest_framework import serializers
from ..models.Department import Department
from ..models.store_management import Store
from ..models.User import User

class DepartmentSerializer(serializers.ModelSerializer):
    admin = serializers.StringRelatedField(read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'admin', 'user_count', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return User.objects.filter(department=obj).count()

class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'description']
    
    def validate_name(self, value):
        """验证部门名称唯一性"""
        if Department.objects.filter(name=value).exists():
            raise serializers.ValidationError("部门名称已存在")
        return value

class DepartmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'description']
    
    def validate_name(self, value):
        """验证部门名称唯一性（排除当前部门）"""
        instance = self.instance
        if Department.objects.filter(name=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError("部门名称已存在")
        return value

class DepartmentAdminChangeSerializer(serializers.Serializer):
    new_admin_email = serializers.EmailField()
    
    def validate_new_admin_email(self, value):
        # 检查邮箱是否已存在用户
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱未注册用户")
        return value

# 从Department_Management.py添加的序列化器
class DepartmentListSerializer(serializers.ModelSerializer):
    """部门列表序列化器（用于列表展示）"""
    member_count = serializers.SerializerMethodField()
    store_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'member_count', 'store_count']
    
    def get_member_count(self, obj):
        """获取部门成员数量"""
        return User.objects.filter(department=obj, is_active=True).count()
    
    def get_store_count(self, obj):
        """获取部门店铺数量"""
        return Store.objects.filter(department=obj).count()

class DepartmentDetailSerializer(serializers.ModelSerializer):
    """部门详情序列化器（用于详细展示）"""
    members = serializers.SerializerMethodField()
    stores = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'members', 'stores']
    
    def get_members(self, obj):
        """获取部门成员信息"""
        members = User.objects.filter(department=obj, is_active=True)
        return [
            {
                'id': member.id,
                'username': member.username,
                'role': member.get_role_display(),
                'phone': member.phone,
                'email': member.email,
                'store': member.store.name if member.store else None,
                'created_at': member.created_at
            }
            for member in members
        ]
    
    def get_stores(self, obj):
        """获取部门店铺信息"""
        stores = Store.objects.filter(department=obj)
        return [
            {
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'created_at': store.created_at
            }
            for store in stores
        ]

class DepartmentMemberSerializer(serializers.ModelSerializer):
    """部门成员序列化器"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'role_display', 'phone', 'email', 'store', 'store_name', 'is_active', 'created_at']

class DepartmentStoreSerializer(serializers.ModelSerializer):
    """部门店铺序列化器"""
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'phone', 'created_at']
