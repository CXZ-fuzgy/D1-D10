# ============================================================
# Day 1 Plus: 终端交互式文件监控器
# 功能: 终端菜单选择模式 → 自动创建或自定义路径 → 启动监控
# ============================================================

import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# -----------------------------------------------------------
# 1. 配置区: 默认参数 (集中管理，方便修改)
# -----------------------------------------------------------
DEFAULT_FOLDER_NAME = "watch_folder"   # 自动模式时创建的默认文件夹名
DEFAULT_LOG_FORMAT = "[{event}] {path}"  # 日志格式模板，{xxx}是占位符


# -----------------------------------------------------------
# 2. 事件处理器 (和之前一样，但加了格式化输出)
# -----------------------------------------------------------
class MyHandler(FileSystemEventHandler):
    """
    文件系统事件处理器
    职责: 当文件夹有变化时，打印格式化的提示信息
    """
    
    def on_created(self, event):
        # 格式化字符串: .format() 方法，把占位符替换成实际值
        print(DEFAULT_LOG_FORMAT.format(event="创建", path=event.src_path))
    
    def on_modified(self, event):
        print(DEFAULT_LOG_FORMAT.format(event="修改", path=event.src_path))
    
    def on_deleted(self, event):
        print(DEFAULT_LOG_FORMAT.format(event="删除", path=event.src_path))


# -----------------------------------------------------------
# 3. 路径管理模块 (核心: 解耦路径获取逻辑)
# -----------------------------------------------------------
class PathManager:
    """
    路径管理器: 负责所有和"文件夹路径"相关的操作
    设计思想: 把"怎么拿到路径"的逻辑封装起来，主程序不用关心细节
    
    为什么用类封装?
    因为路径相关操作有多件: 获取、验证、创建、提示
    放在一起比散落的函数好维护
    """
    
    @staticmethod
    def get_auto_path():
        """
        静态方法: 不需要实例化类就能调用 (PathManager.get_auto_path())
        功能: 在当前脚本所在目录自动创建 watch_folder
        返回: 绝对路径字符串
        """
        # __file__ 是当前文件路径，但用 pyinstaller 打包后可能失效
        # 所以用 os.path.dirname(os.path.abspath(__file__)) 更安全
        current_dir = os.path.dirname(os.path.abspath(__file__))
        auto_path = os.path.join(current_dir, DEFAULT_FOLDER_NAME)
        
        # 确保文件夹存在 (exist_ok=True: 如果已存在不报错)
        os.makedirs(auto_path, exist_ok=True)
        print(f"✅ 自动创建/确认文件夹: {auto_path}")
        return auto_path
    
    @staticmethod
    def get_custom_path():
        """
        功能: 让用户手动输入路径，并验证有效性
        返回: 有效的绝对路径字符串
        """
        while True:  # 无限循环，直到用户输入有效路径
            user_input = input("\n请输入要监控的文件夹路径: ").strip()
            # .strip(): 去掉字符串头尾的空格和换行，防止用户手滑多敲空格
            
            # 展开用户路径中的 ~ 符号 (Linux/Mac 的家目录快捷方式)
            # os.path.expanduser("~/Desktop") → "/home/username/Desktop"
            expanded_path = os.path.expanduser(user_input)
            
            # 转成绝对路径: 把相对路径(如 "./folder")转成完整路径
            absolute_path = os.path.abspath(expanded_path)
            
            # 验证路径是否存在
            if os.path.exists(absolute_path):
                # 验证是否是文件夹 (不是文件)
                if os.path.isdir(absolute_path):
                    print(f"✅ 确认监控路径: {absolute_path}")
                    return absolute_path
                else:
                    print("❌ 这是一个文件，不是文件夹，请重新输入")
            else:
                print(f"❌ 路径不存在: {absolute_path}")
                # 询问是否创建
                choice = input("是否创建此文件夹? (y/n): ").strip().lower()
                # .lower(): 转小写，这样用户输入 Y/y 都能识别
                
                if choice == 'y':
                    os.makedirs(absolute_path, exist_ok=True)
                    print(f"✅ 已创建并监控: {absolute_path}")
                    return absolute_path
                # 如果用户选 n，while 循环继续，重新要求输入
    
    @staticmethod
    def get_custom_and_create():
        """
        组合功能: 自定义路径 + 在该路径下自动创建子文件夹
        返回: 新创建的子文件夹绝对路径
        """
        # 先拿到用户指定的父目录
        parent_path = PathManager.get_custom_path()
        
        # 在父目录下创建默认名称的子文件夹
        new_folder = os.path.join(parent_path, DEFAULT_FOLDER_NAME)
        os.makedirs(new_folder, exist_ok=True)
        print(f"✅ 在 {parent_path} 下创建监控文件夹: {new_folder}")
        return new_folder


# -----------------------------------------------------------
# 4. 终端交互菜单 (核心: 状态机思想的雏形)
# -----------------------------------------------------------
class TerminalMenu:
    """
    终端菜单: 负责和用户交互，收集选择，返回结果
    设计思想: 把"交互逻辑"和"业务逻辑"分离
    
    状态机雏形:
    状态1: 显示菜单 → 等待输入 → 根据输入跳转到不同分支
    每个分支处理完，要么结束，要么回到状态1
    """
    
    @staticmethod
    def show_menu():
        """
        显示主菜单，返回用户选择 (字符串)
        """
        print("\n" + "=" * 40)
        print("      📁 文件监控器启动菜单")
        print("=" * 40)
        print("  [1] 自动模式: 在当前目录创建 watch_folder")
        print("  [2] 自定义模式: 输入现有文件夹路径")
        print("  [3] 组合模式: 指定位置 + 自动创建子文件夹")
        print("  [q] 退出程序")
        print("=" * 40)
        
        # 获取用户输入
        choice = input("请选择模式 (1/2/3/q): ").strip().lower()
        return choice
    
    @staticmethod
    def handle_choice(choice: str) -> str | None:
        """
        处理用户选择，返回最终要监控的路径，或 None 表示退出
        参数类型提示: choice: str 表示"这个参数应该是字符串"
        返回值: str | None 表示"返回字符串或None"
        
        这就是"分发逻辑": 根据输入，分发到不同的处理函数
        """
        # 使用 match-case (Python 3.10+) 或 if-elif 做分支
        # match-case 比 if-elif 更清晰，适合多分支场景
        
        if choice == '1':
            # 自动模式
            return PathManager.get_auto_path()
            
        elif choice == '2':
            # 自定义模式
            return PathManager.get_custom_path()
            
        elif choice == '3':
            # 组合模式
            return PathManager.get_custom_and_create()
            
        elif choice in ('q', 'quit', 'exit'):
            # 退出: 返回 None，上层代码收到 None 就结束程序
            print("👋 再见!")
            return None
            
        else:
            # 无效输入: 打印错误，返回空字符串表示"需要重新显示菜单"
            print("❌ 无效选项，请重新选择")
            return ""  # 空字符串是"重试信号"，不是None的"退出信号"


# -----------------------------------------------------------
# 5. 监控引擎 (和之前一样，但封装成类)
# -----------------------------------------------------------
class MonitorEngine:
    """
    监控引擎: 负责启动和停止 watchdog
    封装目的: 主程序只需要说"开始监控这个路径"，不用关心底层线程
    """
    
    def __init__(self, watch_path: str):
        # __init__: 构造函数，创建实例时自动执行
        # self: 实例自身的引用，每个实例有自己的数据
        self.watch_path = watch_path      # 实例变量: 这个监控器盯哪个文件夹
        self.observer = None              # 实例变量: 占位，后面赋值
    
    def start(self):
        """
        启动监控，阻塞运行直到用户按Ctrl+C
        """
        # 创建事件处理器
        handler = MyHandler()
        
        # 创建并配置监控器
        self.observer = Observer()
        self.observer.schedule(handler, self.watch_path, recursive=True)
        
        # 启动后台线程
        self.observer.start()
        print(f"\n🔴 正在监控: {self.watch_path}")
        print("   提示: 往这个文件夹里添加/修改/删除文件，看这里输出")
        print("   按 Ctrl+C 停止监控\n")
        
        try:
            # 主线程保持存活，同时observer后台线程在工作
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号...")
        finally:
            # finally: 无论try里发生什么(包括异常)，都会执行
            # 确保资源一定被释放，不会留下"僵尸线程"
            self.stop()
    
    def stop(self):
        """
        安全停止监控
        """
        if self.observer:
            self.observer.stop()   # 通知停止
            self.observer.join()   # 等待真正结束
            print("✅ 监控已安全停止")


# -----------------------------------------------------------
# 6. 主程序: 组装所有模块 (核心: 控制流程)
# -----------------------------------------------------------
def main():

    
    print("欢迎使用文件监控器!")
    
    while True:  # 外层循环: 允许监控结束后重新选择模式
        # 步骤1&2: 显示菜单，处理选择
        choice = TerminalMenu.show_menu()
        watch_path = TerminalMenu.handle_choice(choice)
        
        # 解析返回值
        if watch_path is None:
            # None = 用户选择退出
            break
            
        if watch_path == "":
            # 空字符串 = 无效输入，直接回到菜单 (continue 跳过本次循环剩余代码)
            continue
        
        # 步骤3: 拿到有效路径，启动监控
        engine = MonitorEngine(watch_path)
        engine.start()
        
        # 监控结束后，询问是否继续
        print("\n" + "-" * 40)
        again = input("监控已结束。是否监控其他文件夹? (y/n): ").strip().lower()
        if again != 'y':
            print("👋 程序结束")
            break


# -----------------------------------------------------------
# 7. 程序入口
# -----------------------------------------------------------
if __name__ == "__main__":
    main()
