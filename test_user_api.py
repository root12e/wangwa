#!/usr/bin/env python3
"""
用户管理API测试脚本
用于测试后端API是否正常工作
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:8000"

def test_api_endpoint(endpoint, method="GET", data=None, headers=None):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"不支持的HTTP方法: {method}")
            return False
            
        print(f"\n=== 测试 {method} {endpoint} ===")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"响应文本: {response.text}")
            
        return response.status_code < 400
        
    except requests.exceptions.ConnectionError:
        print(f"连接失败: 无法连接到 {url}")
        return False
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("开始测试用户管理API...")
    
    # 测试基础端点
    endpoints = [
        ("/api/users/", "GET"),
        ("/api/users/statistics/", "GET"),
        ("/api/departments/", "GET"),
        ("/api/stores/", "GET"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, method in endpoints:
        if test_api_endpoint(endpoint, method):
            success_count += 1
        else:
            print(f"❌ {endpoint} 测试失败")
    
    print(f"\n=== 测试结果 ===")
    print(f"成功: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ 所有API端点测试通过")
        return True
    else:
        print("❌ 部分API端点测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
