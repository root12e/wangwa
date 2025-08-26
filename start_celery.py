#!/usr/bin/env python
"""
Celery启动脚本
用于启动库存管理系统的定时任务
"""

import os
import sys
import subprocess
import time
import signal
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/celery.log')
    ]
)

logger = logging.getLogger(__name__)

class CeleryManager:
    """Celery管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = []
        
    def start_worker(self, queue='inventory', concurrency=2):
        """启动工作进程"""
        cmd = [
            'celery', '-A', 'wwkc', 'worker',
            '--loglevel=info',
            '--queues=' + queue,
            '--concurrency=' + str(concurrency),
            '--hostname=worker@%h',
            '--pool=prefork',
            '--max-tasks-per-child=1000',
            '--max-memory-per-child=200000'
        ]
        
        logger.info(f"启动工作进程: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, cwd=self.project_root)
        self.processes.append(('worker', process))
        return process
    
    def start_beat(self):
        """启动定时任务调度器"""
        cmd = [
            'celery', '-A', 'wwkc', 'beat',
            '--loglevel=info',
            '--scheduler=django_celery_beat.schedulers:DatabaseScheduler',
            '--pidfile=logs/celerybeat.pid'
        ]
        
        logger.info(f"启动定时任务调度器: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, cwd=self.project_root)
        self.processes.append(('beat', process))
        return process
    
    def start_flower(self, port=5555):
        """启动监控界面"""
        cmd = [
            'celery', '-A', 'wwkc', 'flower',
            '--port=' + str(port),
            '--loglevel=info',
            '--url_prefix=flower'
        ]
        
        logger.info(f"启动监控界面: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, cwd=self.project_root)
        self.processes.append(('flower', process))
        return process
    
    def start_all(self, concurrency=2, flower_port=5555):
        """启动所有服务"""
        logger.info("开始启动Celery服务...")
        
        # 创建日志目录
        log_dir = self.project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        try:
            # 启动工作进程
            self.start_worker(concurrency=concurrency)
            time.sleep(2)
            
            # 启动定时任务调度器
            self.start_beat()
            time.sleep(2)
            
            # 启动监控界面
            self.start_flower(port=flower_port)
            time.sleep(2)
            
            logger.info("所有Celery服务启动完成")
            logger.info(f"监控界面: http://localhost:{flower_port}/flower")
            
            # 等待进程
            self.wait_for_processes()
            
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭服务...")
            self.stop_all()
        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            self.stop_all()
            sys.exit(1)
    
    def wait_for_processes(self):
        """等待所有进程"""
        try:
            while True:
                # 检查进程状态
                for name, process in self.processes:
                    if process.poll() is not None:
                        logger.warning(f"{name} 进程已退出，退出码: {process.returncode}")
                
                # 移除已退出的进程
                self.processes = [(name, p) for name, p in self.processes if p.poll() is None]
                
                if not self.processes:
                    logger.warning("所有进程已退出")
                    break
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("收到停止信号")
            self.stop_all()
    
    def stop_all(self):
        """停止所有服务"""
        logger.info("正在停止所有Celery服务...")
        
        for name, process in self.processes:
            try:
                logger.info(f"停止 {name} 进程 (PID: {process.pid})")
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"{name} 进程未在10秒内结束，强制终止")
                    process.kill()
                    process.wait()
                    
            except Exception as e:
                logger.error(f"停止 {name} 进程失败: {e}")
        
        self.processes.clear()
        logger.info("所有服务已停止")
    
    def status(self):
        """查看服务状态"""
        logger.info("Celery服务状态:")
        
        for name, process in self.processes:
            if process.poll() is None:
                logger.info(f"  {name}: 运行中 (PID: {process.pid})")
            else:
                logger.info(f"  {name}: 已退出 (退出码: {process.returncode})")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Celery服务管理器')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'worker', 'beat', 'flower'],
                       help='要执行的命令')
    parser.add_argument('--concurrency', type=int, default=2,
                       help='工作进程并发数 (默认: 2)')
    parser.add_argument('--port', type=int, default=5555,
                       help='监控界面端口 (默认: 5555)')
    parser.add_argument('--queue', default='inventory',
                       help='工作队列名称 (默认: inventory)')
    
    args = parser.parse_args()
    
    manager = CeleryManager()
    
    if args.command == 'start':
        manager.start_all(concurrency=args.concurrency, flower_port=args.port)
    elif args.command == 'worker':
        manager.start_worker(queue=args.queue, concurrency=args.concurrency)
        manager.wait_for_processes()
    elif args.command == 'beat':
        manager.start_beat()
        manager.wait_for_processes()
    elif args.command == 'flower':
        manager.start_flower(port=args.port)
        manager.wait_for_processes()
    elif args.command == 'status':
        manager.status()
    elif args.command == 'stop':
        manager.stop_all()

if __name__ == '__main__':
    main()
