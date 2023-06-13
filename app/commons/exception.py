import time
import datetime
import traceback


class PackageError(Exception):
    def __init__(self, message):
        self.message = message


class NetworkError(PackageError):
    """网络错误"""
    pass


# 依赖错误
class DependencyError(PackageError):
    """依赖错误"""
    pass


class ConfigError(PackageError):
    """配置错误"""
    pass


def record(step=''):
    def decorator(func):
        def wrapper(*args, **kwargs):
            step_name = step if step else func.__name__
            ins = args[0]
            start_time = time.time()
            ins.out_put_report(
                f"【{step_name}执行开始】-{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            try:
                result = func(*args, **kwargs)
            except (Exception,) as e:
                ins.out_put_report(f'【{step_name}执行异常:{str(e)}】')
                ins.logger.error(f'【{step_name}执行异常:{str(e)}】')
                ins.logger.error(f'【{step_name}执行异常:{traceback.format_exc()}】')
                raise e
            finally:
                end_time = time.time()
                end_time_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ins.out_put_report(
                    f"【{step_name}执行完成于{end_time_format},共耗时{end_time - start_time:.2f}秒】"
                )
            return result

        return wrapper

    return decorator
