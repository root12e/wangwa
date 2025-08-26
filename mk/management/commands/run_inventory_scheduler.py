from django.core.management.base import BaseCommand
from django.utils import timezone
import time
import logging
from mk.services.scheduler_service import SchedulerService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """库存定时任务管理命令"""
    
    help = '运行库存管理定时任务，自动执行扣子工作流'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='以守护进程模式运行，持续监控和执行任务'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='执行间隔（秒），默认300秒（5分钟）'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='只执行一次，不循环执行'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制执行，忽略时间间隔检查'
        )
    
    def handle(self, *args, **options):
        """命令执行入口"""
        try:
            scheduler = SchedulerService()
            
            # 更新执行间隔
            if options['interval'] != 300:
                scheduler.update_execution_interval(options['interval'])
                self.stdout.write(
                    self.style.SUCCESS(f'执行间隔已更新为 {options["interval"]} 秒')
                )
            
            if options['once']:
                # 只执行一次
                self.stdout.write('开始执行一次工作流...')
                result = scheduler.execute_scheduled_workflow()
                self._print_result(result)
                return
            
            if options['force']:
                # 强制执行
                self.stdout.write('开始强制执行工作流...')
                result = scheduler.force_execute_workflow()
                self._print_result(result)
                return
            
            if options['daemon']:
                # 守护进程模式
                self.stdout.write('开始以守护进程模式运行库存定时任务...')
                self.stdout.write(f'执行间隔: {scheduler.execution_interval} 秒')
                self.stdout.write('按 Ctrl+C 停止任务')
                
                try:
                    while True:
                        self._run_scheduled_task(scheduler)
                        time.sleep(60)  # 每分钟检查一次
                        
                except KeyboardInterrupt:
                    self.stdout.write(self.style.WARNING('\n收到停止信号，正在退出...'))
                    return
            else:
                # 交互模式
                self.stdout.write('开始运行库存定时任务...')
                self.stdout.write(f'执行间隔: {scheduler.execution_interval} 秒')
                self.stdout.write('按 Enter 键手动执行，按 Ctrl+C 退出')
                
                try:
                    while True:
                        try:
                            # 等待用户输入
                            user_input = input('\n按 Enter 键执行任务，输入 "status" 查看状态，输入 "quit" 退出: ').strip()
                            
                            if user_input.lower() == 'quit':
                                break
                            elif user_input.lower() == 'status':
                                self._show_status(scheduler)
                            elif user_input == '':
                                self._run_scheduled_task(scheduler)
                            else:
                                self.stdout.write('无效输入，请按 Enter 键执行任务，输入 "status" 查看状态，或输入 "quit" 退出')
                                
                        except EOFError:
                            break
                            
                except KeyboardInterrupt:
                    self.stdout.write(self.style.WARNING('\n收到停止信号，正在退出...'))
                    return
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'运行定时任务失败: {str(e)}')
            )
            logger.error(f'运行定时任务失败: {str(e)}')
    
    def _run_scheduled_task(self, scheduler):
        """运行定时任务"""
        try:
            self.stdout.write(f'\n[{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}] 检查是否需要执行工作流...')
            
            # 检查是否应该执行
            if scheduler.should_execute_workflow():
                self.stdout.write('开始执行定时工作流...')
                result = scheduler.execute_scheduled_workflow()
                self._print_result(result)
            else:
                # 获取下次执行时间
                next_execution_info = scheduler.get_next_execution_time()
                if next_execution_info.get('next_execution'):
                    next_time = next_execution_info['next_execution']
                    time_until = next_execution_info['time_until_next']
                    self.stdout.write(
                        self.style.WARNING(
                            f'未到执行时间，下次执行: {next_time.strftime("%Y-%m-%d %H:%M:%S")} '
                            f'(还有 {int(time_until)} 秒)'
                        )
                    )
                else:
                    self.stdout.write('无法获取下次执行时间')
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'执行定时任务失败: {str(e)}')
            )
            logger.error(f'执行定时任务失败: {str(e)}')
    
    def _show_status(self, scheduler):
        """显示状态信息"""
        try:
            status = scheduler.get_scheduler_status()
            
            if "error" in status:
                self.stdout.write(
                    self.style.ERROR(f'获取状态失败: {status["error"]}')
                )
                return
            
            self.stdout.write('\n=== 定时任务状态 ===')
            self.stdout.write(f'执行间隔: {status["scheduler"]["execution_interval"]} 秒')
            self.stdout.write(f'总批次: {status["scheduler"]["total_batches"]}')
            self.stdout.write(f'完成批次: {status["scheduler"]["completed_batches"]}')
            self.stdout.write(f'失败批次: {status["scheduler"]["failed_batches"]}')
            
            if status["scheduler"]["next_execution"]:
                next_time = status["scheduler"]["next_execution"]
                time_until = status["scheduler"]["time_until_next"]
                self.stdout.write(
                    f'下次执行: {next_time.strftime("%Y-%m-%d %H:%M:%S")} '
                    f'(还有 {int(time_until)} 秒)'
                )
            
            if status["scheduler"]["last_execution"]:
                last_time = status["scheduler"]["last_execution"]
                self.stdout.write(
                    f'上次执行: {last_time.strftime("%Y-%m-%d %H:%M:%S")}'
                )
            
            self.stdout.write('\n=== 订单统计 ===')
            self.stdout.write(f'总订单: {status["orders"]["total"]}')
            self.stdout.write(f'已处理: {status["orders"]["processed"]}')
            self.stdout.write(f'未处理: {status["orders"]["unprocessed"]}')
            
            self.stdout.write('\n=== 工作流状态 ===')
            workflow_status = status["workflow"]
            if "error" not in workflow_status:
                self.stdout.write(f'总订单: {workflow_status.get("total_orders", 0)}')
                self.stdout.write(f'已处理: {workflow_status.get("processed_orders", 0)}')
                self.stdout.write(f'未处理: {workflow_status.get("unprocessed_orders", 0)}')
                
                if workflow_status.get("last_execution"):
                    last_exec = workflow_status["last_execution"]
                    self.stdout.write(
                        f'最后执行: {last_exec["execution_time"].strftime("%Y-%m-%d %H:%M:%S")} '
                        f'(批次: {last_exec["batch_id"]})'
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'获取工作流状态失败: {workflow_status["error"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'获取状态失败: {str(e)}')
            )
            logger.error(f'获取状态失败: {str(e)}')
    
    def _print_result(self, result):
        """打印执行结果"""
        if result["success"]:
            self.stdout.write(
                self.style.SUCCESS(f'执行成功: {result.get("message", "")}')
            )
            
            if "workflow_result" in result:
                workflow = result["workflow_result"]
                self.stdout.write(f'  工作流结果: 获取 {workflow.get("total_orders", 0)} 个订单')
                self.stdout.write(f'  执行时间: {workflow.get("execution_time", 0):.2f} 秒')
                self.stdout.write(f'  批次ID: {workflow.get("batch_id", "")}')
            
            if "inventory_result" in result:
                inventory = result["inventory_result"]
                self.stdout.write(f'  库存处理: 成功 {inventory.get("success_count", 0)} 个，失败 {inventory.get("failed_count", 0)} 个')
                
        else:
            self.stdout.write(
                self.style.ERROR(f'执行失败: {result.get("message", "")}')
            )
            
            if "error" in result:
                self.stdout.write(f'  错误详情: {result["error"]}')
