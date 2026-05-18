# day1_project.py
# D1 目标：监控文件夹，新图片进来就报告详细信息

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# ========== 配置区 ==========
INPUT_DIR = Path("D:\D1-D10\测试0-1")          # 监控的文件夹
INPUT_DIR.mkdir(exist_ok=True)              # 不存在就创建

VALID_EXT = {'.jpg', '.jpeg', '.png'}       # 支持的图片后缀（集合，查找快）

# ========== 处理器 ==========
class ImageWatcher(FileSystemEventHandler):
    """
    继承 FileSystemEventHandler，只关心图片文件
    """
    
    def on_created(self, event):
        # event.is_directory: 判断变化的是不是文件夹
        if event.is_directory:
            return  # 文件夹变化忽略
        
        # event.src_path: 变化的文件路径（字符串）
        file_path = Path(event.src_path)
        
        # 检查后缀（.suffix 返回如 '.jpg'，转小写比较）
        if file_path.suffix.lower() not in VALID_EXT:
            print(f"⏭ 忽略非图片: {file_path.name}")
            return
        
        # 获取文件信息
        size = file_path.stat().st_size         # 文件大小（字节）
        abs_path = file_path.resolve()          # 绝对路径
        
        print(f"\n{'='*40}")
        print(f" 检测到新图片")
        print(f"   文件名: {file_path.name}")
        print(f"   纯名称: {file_path.stem}")
        print(f"   后缀: {file_path.suffix}")
        print(f"   大小: {size:,} bytes ({size/1024:.1f} KB)")
        print(f"   绝对路径: {abs_path}")
        print(f"{'='*40}")

# ========== 主程序 ==========
def main():
    print(f" 文件夹监控启动")
    print(f" 监控路径: {INPUT_DIR.resolve()}")
    print(f" 支持格式: {', '.join(VALID_EXT)}")
    print(f" 测试方法: 拖一张图片进上面的文件夹")
    print(f" 退出: 按 Ctrl+C\n")
    
    # 初始化观察器
    observer = Observer()
    
    # 绑定：处理器 + 路径 + 不递归
    observer.schedule(ImageWatcher(), path=str(INPUT_DIR), recursive=False)
    
    # 启动后台线程
    observer.start()
    
    # 主线程保持存活
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n 收到停止信号...")
        observer.stop()
    
    # 等待后台线程清理完毕
    observer.join()
    print(" 已退出")

if __name__ == "__main__":
    main()
