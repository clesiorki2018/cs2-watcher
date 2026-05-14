import keyboard
from pynput import mouse

from cs2watcher.watcher import AccessibilityWatcher


def main():
    watcher = AccessibilityWatcher.build_default()
    config = watcher.config

    print("===================================")
    print(" Accessibility Watcher")
    print("===================================")
    print(f"{config.hotkey_main_mode} -> Ativar/desativar")
    print(f"{config.hotkey_side_mode} -> Ativar/desativar lateral")
    print(f"{config.hotkey_exit} -> Sair")
    print("")

    mouse_listener = mouse.Listener(
        on_click=watcher.handle_click,
    )
    mouse_listener.start()

    keyboard.add_hotkey(
        config.hotkey_main_mode,
        watcher.toggle_main_mode,
    )
    keyboard.add_hotkey(
        config.hotkey_side_mode,
        watcher.toggle_side_movement,
    )

    try:
        keyboard.wait(config.hotkey_exit)
    finally:
        print("Finalizando...")
        watcher.shutdown()
        mouse_listener.stop()


if __name__ == "__main__":
    main()
