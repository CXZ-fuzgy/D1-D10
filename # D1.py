# 1. 导入时间模块，用来让程序“休眠”（后面用于保持程序运行）
import time

# 2. 导入 pathlib 模块，用它来更优雅地处理文件和文件夹路径
import pathlib

# 3. 从 watchdog.observers 导入 Observer，这是监控文件夹的核心“警卫”
from watchdog.observers import Observer

# 4. 从 watchdog.events 导入 FileSystemEventHandler，这是我们要继承并改造的基础“处理器”
from watchdog.events import FileSystemEventHandler

# ----------------------- 配置区域 -----------------------

# 5. 设置我们要监控的文件夹路径（使用 pathlib.Path）
INPUT_DIR = pathlib.Path("D:/D1-D10/测试0-1")

# 6. 如果上面路径对应的文件夹不存在，就自动创建它（防止程序报错）
INPUT_DIR.mkdir(exist_ok=True)

# 7. 定义一个列表，里面放所有我们关心的文件后缀名（只监控图片）
VALID_EXT = ['.jpg', '.jpeg', '.png']

# ----------------------- 处理器类定义 -----------------------

# 8. 定义一个类，继承 FileSystemEventHandler，用来自定义“当文件发生变化时做什么”
class ImageWatcher(FileSystemEventHandler):

    # 9. 定义 on_created 方法，当有“新文件被创建”时自动触发
    def on_created(self, event):
        # 10. 判断事件是不是关于文件夹（不是具体文件）的创建
        if event.is_directory:
            # 11. 如果是文件夹，直接结束这个方法（我们不关心文件夹）
            return

        # 12. 拿到被创建的文件的路径（用 pathlib 转换一下）
        file_path = pathlib.Path(event.src_path)

        # 13. 获取文件的后缀名（比如 .jpg），并统一转成小写（方便对比）
        # 14. 如果后缀名不在我们的白名单 VALID_EXT 里
        if file_path.suffix.lower() not in VALID_EXT:
            # 15. 那就忽略它，不做任何处理（比如放进去的是 .txt 文件就直接跳过）
            return

        # 16. 获取文件的大小（字节数）
        size = file_path.stat().st_size
        # 17. 获取文件的绝对路径（比如 D:/... 这种完整写法）
        abs_path = file_path.resolve()

        # 18. 开始打印信息（用分隔线让输出更好看）
        print(f"\\n{'='*40}")
        # 19. 打印提示“监控到新文件”
        print(f"[监控到新文件]")
        # 20. 打印文件名（比如 cat.jpg）
        print(f"文件名: {file_path.name}")
        # 21. 打印文件后缀名
        print(f"后缀名: {file_path.suffix}")
        # 22. 打印文件的绝对路径
        print(f"完整路径: {abs_path}")
        # 23. 打印文件大小（单位：字节）
        print(f"文件大小: {size} bytes")
        # 24. 打印底部分割线
        print(f"{'='*40}")

# ----------------------- 主程序入口 -----------------------

# 25. 定义 main 函数，它是程序执行的起点
def main():
    # 26. 打印提示信息，告诉用户正在监控哪个文件夹
    print(f"正在监控文件夹: {INPUT_DIR}")
    # 27. 提示用户自己去放图片测试
    print("请把图片放进去查看效果...")

    # 28. 创建 Observer 对象（可以理解为一个“巡警”）
    observer = Observer()
    
    # 29. 给“巡警”安排任务：当 INPUT_DIR 里发生文件变化时，用 ImageWatcher 去处理
    # 30. recursive=False 表示不监控子文件夹（只监控当前这一层）
    observer.schedule(ImageWatcher(), path=str(INPUT_DIR), recursive=False)

    # 31. 让“巡警”开始巡逻（启动监控）
    observer.start()

    # 32. 使用 try...except 结构，方便我们用 Ctrl+C 安全关闭程序
    try:
        # 33. 无限循环（保持主程序不退出）
        while True:
            # 34. 每次循环睡 1 秒（节省电脑 CPU 资源）
            time.sleep(1)
    # 35. 如果用户按下键盘上的 Ctrl+C（中断信号）
    except KeyboardInterrupt:
        # 36. 打印提示“检测到关闭信号...”
        print("检测到关闭信号...")
        # 37. 告诉“巡警”停止巡逻
        observer.stop()

    # 38. 等“巡警”完全停止工作后再退出（防止文件未处理完）
    observer.join()
    # 39. 打印“程序已退出”
    print("程序已退出")

# 40. 判断是否直接运行这个脚本（而不是被其他文件导入）
if __name__ == "__main__":
    # 41. 如果是直接运行，就执行 main() 函数
    main()