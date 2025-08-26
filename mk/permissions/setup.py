"""
权限管理包安装配置
"""

from setuptools import setup, find_packages

setup(
    name="mk-permissions",
    version="1.0.0",
    description="完整的权限管理系统，按功能模块组织",
    author="WWKC Team",
    author_email="team@wwkc.com",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2",
        "djangorestframework>=3.12",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    keywords="django permissions security access-control",
    project_urls={
        "Documentation": "https://github.com/wwkc/mk-permissions",
        "Source": "https://github.com/wwkc/mk-permissions",
        "Tracker": "https://github.com/wwkc/mk-permissions/issues",
    },
)
