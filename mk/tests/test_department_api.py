#!/usr/bin/env python3
"""
部门管理API测试脚本
用于测试部门管理的各项功能
"""

import requests
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_result(title, success, message=""):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    print(f"{title}: {status}")
    if message:
        print(f"   {message}")

def test_department_list():
    """测试获取部门列表"""
    print_section("测试获取部门列表")
    
    try:
        response = requests.get(f"{API_BASE}/departments/")
        if response.status_code == 200:
            data = response.json()
            print_result("获取部门列表", True, f"共找到 {data.get('count', 0)} 个部门")
            
            # 显示部门信息
            for dept in data.get('results', [])[:3]:  # 只显示前3个
                print(f"  • {dept['name']}: {dept['member_count']} 个成员, {dept['store_count']} 个店铺")
            
            return True
        else:
            print_result("获取部门列表", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("获取部门列表", False, f"异常: {str(e)}")
        return False

def test_department_detail():
    """测试获取部门详情"""
    print_section("测试获取部门详情")
    
    try:
        # 先获取部门列表
        response = requests.get(f"{API_BASE}/departments/")
        if response.status_code != 200:
            print_result("获取部门详情", False, "无法获取部门列表")
            return False
        
        departments = response.json().get('results', [])
        if not departments:
            print_result("获取部门详情", False, "没有找到部门")
            return False
        
        # 获取第一个部门的详情
        dept_id = departments[0]['id']
        response = requests.get(f"{API_BASE}/departments/{dept_id}/")
        
        if response.status_code == 200:
            data = response.json()
            print_result("获取部门详情", True, f"部门: {data['name']}")
            print(f"  成员数量: {len(data.get('members', []))}")
            print(f"  店铺数量: {len(data.get('stores', []))}")
            return True
        else:
            print_result("获取部门详情", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("获取部门详情", False, f"异常: {str(e)}")
        return False

def test_department_members():
    """测试获取部门成员"""
    print_section("测试获取部门成员")
    
    try:
        # 先获取部门列表
        response = requests.get(f"{API_BASE}/departments/")
        if response.status_code != 200:
            print_result("获取部门成员", False, "无法获取部门列表")
            return False
        
        departments = response.json().get('results', [])
        if not departments:
            print_result("获取部门成员", False, "没有找到部门")
            return False
        
        # 获取第一个部门的成员
        dept_id = departments[0]['id']
        response = requests.get(f"{API_BASE}/departments/{dept_id}/members/")
        
        if response.status_code == 200:
            data = response.json()
            print_result("获取部门成员", True, f"共 {data.get('count', 0)} 个成员")
            
            # 显示成员信息
            for member in data.get('results', [])[:3]:  # 只显示前3个
                print(f"  • {member['username']} ({member['role_display']})")
            
            return True
        else:
            print_result("获取部门成员", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("获取部门成员", False, f"异常: {str(e)}")
        return False

def test_department_stores():
    """测试获取部门店铺"""
    print_section("测试获取部门店铺")
    
    try:
        # 先获取部门列表
        response = requests.get(f"{API_BASE}/departments/")
        if response.status_code != 200:
            print_result("获取部门店铺", False, "无法获取部门列表")
            return False
        
        departments = response.json().get('results', [])
        if not departments:
            print_result("获取部门店铺", False, "没有找到部门")
            return False
        
        # 获取第一个部门的店铺
        dept_id = departments[0]['id']
        response = requests.get(f"{API_BASE}/departments/{dept_id}/stores/")
        
        if response.status_code == 200:
            data = response.json()
            print_result("获取部门店铺", True, f"共 {data.get('count', 0)} 个店铺")
            
            # 显示店铺信息
            for store in data.get('results', [])[:3]:  # 只显示前3个
                print(f"  • {store['name']}: {store['address']}")
            
            return True
        else:
            print_result("获取部门店铺", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("获取部门店铺", False, f"异常: {str(e)}")
        return False

def test_department_statistics():
    """测试获取部门统计信息"""
    print_section("测试获取部门统计信息")
    
    try:
        # 先获取部门列表
        response = requests.get(f"{API_BASE}/departments/")
        if response.status_code != 200:
            print_result("获取部门统计", False, "无法获取部门列表")
            return False
        
        departments = response.json().get('results', [])
        if not departments:
            print_result("获取部门统计", False, "没有找到部门")
            return False
        
        # 获取第一个部门的统计信息
        dept_id = departments[0]['id']
        response = requests.get(f"{API_BASE}/departments/{dept_id}/statistics/")
        
        if response.status_code == 200:
            data = response.json()
            print_result("获取部门统计", True, f"部门: {data['department_name']}")
            print(f"  总用户数: {data['total_users']}")
            print(f"  总店铺数: {data['total_stores']}")
            
            # 显示用户统计
            for role, stats in data.get('user_statistics', {}).items():
                print(f"  {stats['name']}: {stats['count']} 人")
            
            return True
        else:
            print_result("获取部门统计", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("获取部门统计", False, f"异常: {str(e)}")
        return False

def test_department_search():
    """测试部门搜索功能"""
    print_section("测试部门搜索功能")
    
    try:
        # 搜索包含"技术"的部门
        response = requests.get(f"{API_BASE}/departments/search/?q=技术")
        
        if response.status_code == 200:
            data = response.json()
            print_result("部门搜索", True, f"找到 {data.get('count', 0)} 个结果")
            
            # 显示搜索结果
            for dept in data.get('results', []):
                print(f"  • {dept['name']}: {dept['description']}")
            
            return True
        else:
            print_result("部门搜索", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_result("部门搜索", False, f"异常: {str(e)}")
        return False

def test_unauthorized_operations():
    """测试未授权操作"""
    print_section("测试未授权操作")
    
    try:
        # 尝试创建部门（无认证）
        new_dept = {
            "name": "测试部门",
            "description": "这是一个测试部门"
        }
        response = requests.post(f"{API_BASE}/departments/", json=new_dept)
        
        if response.status_code in [401, 403]:
            print_result("未授权创建部门", True, "正确拒绝未授权请求")
        else:
            print_result("未授权创建部门", False, f"意外允许，状态码: {response.status_code}")
        
        return True
    except Exception as e:
        print_result("未授权创建部门", False, f"异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("部门管理API测试开始")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试地址: {BASE_URL}")
    
    # 测试列表
    tests = [
        test_department_list,
        test_department_detail,
        test_department_members,
        test_department_stores,
        test_department_statistics,
        test_department_search,
        test_unauthorized_operations,
    ]
    
    # 执行测试
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"{test.__name__}: ❌ 异常 - {str(e)}")
    
    # 输出测试结果
    print_section("测试结果汇总")
    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        sys.exit(1)
