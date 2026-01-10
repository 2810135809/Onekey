import os
import sys
import threading
import webview

from pathlib import Path
from PIL import Image

from src.config import ConfigManager
from src.utils.i18n import t

project_root = Path(__file__)
config_manager = ConfigManager()
sys.path.insert(0, str(project_root))
window = webview.create_window(
    title="Onekey",
    url=f"http://localhost:{config_manager.app_config.port}",
    width=1600,
    height=900,
)


def hide_console() -> None:
    """隐藏控制台窗口"""
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        console_window = kernel32.GetConsoleWindow()
        if console_window:
            user32.ShowWindow(console_window, 0)  # SW_HIDE = 0
    except Exception:
        pass


def create_icon() -> Image.Image:
    """创建托盘图标"""
    try:
        return Image.open(project_root.parent / "icon.jpg")
    except Exception as e:
        if config_manager.app_config.show_console:
            print(t("error.load_icon", error=str(e)))
        # 创建默认图标
        return Image.new("RGBA", (32, 32), color=(103, 80, 164, 255))


def create_system_tray() -> bool:
    """创建系统托盘"""
    try:
        import pystray

        def on_quit(icon, item):
            icon.stop()
            os._exit(0)

        def on_show_window(icon, item):
            window.show()

        def on_show_console(icon, item):
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32
                user32 = ctypes.windll.user32
                console_window = kernel32.GetConsoleWindow()
                if console_window:
                    user32.ShowWindow(console_window, 1)  # SW_NORMAL = 1
            except Exception:
                pass

        # 创建托盘菜单
        menu = pystray.Menu(
            pystray.MenuItem(t("tray.show_window"), on_show_window),
            pystray.MenuItem(t("tray.show_console"), on_show_console),
            pystray.MenuItem(t("tray.exit"), on_quit),
        )

        # 创建托盘图标
        icon = pystray.Icon("Onekey", create_icon(), menu=menu)

        # 在单独的线程中运行托盘
        def run_tray():
            icon.run()

        tray_thread = threading.Thread(target=run_tray)
        tray_thread.daemon = True
        tray_thread.start()

        return True
    except ImportError:
        return False


def start_web_server() -> None:
    """启动Web服务器"""
    from web.app import app
    from uvicorn import Config
    from uvicorn.server import Server

    server = Server(
        Config(
            app, host="0.0.0.0", port=config_manager.app_config.port, log_level="error"
        )
    )
    server.run()


def main() -> None:
    """主函数"""
    try:
        config = config_manager.app_config
        show_console = config.show_console

        if show_console:
            print(t("main.starting"))
            print("=" * 50)

        # 处理控制台显示
        if not show_console:
            hide_console()
            tray_created = create_system_tray()
        else:
            tray_created = create_system_tray()
            if tray_created:
                print(t("main.tray_created"))

        def on_closing():
            if window.create_confirmation_dialog("Onekey", "是否关闭Onekey"):
                os._exit(0)
            return False

        window.events.closing += on_closing

        # 启动浏览器
        webview.start(func=start_web_server)
    except KeyboardInterrupt:
        if config_manager.app_config.show_console:
            print(f"\n{t('main.exit')}")
    except Exception as e:
        if config_manager.app_config.show_console:
            print(t("main.start_error", error=str(e)))
            input(t("main.press_enter"))
        else:
            # 在隐藏控制台模式下记录错误
            error_log = Path("error.log")
            with open(error_log, "w", encoding="utf-8") as f:
                f.write(t("main.startup_failed", error=str(e)) + "\n")


if __name__ == "__main__":
    main()
