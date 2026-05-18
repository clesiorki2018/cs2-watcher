# Copyright 2026 Clesiorki
# SPDX-License-Identifier: Apache-2.0

from pynput import mouse

from cs2watcher.hotkeys import HotkeyListener
from cs2watcher.watcher import AccessibilityWatcher


def main():
    # constroi os servicos antes de abrir listeners do sistema.
    watcher = AccessibilityWatcher.build_default()
    config = watcher.config

    print("===================================")
    print(" Accessibility Watcher")
    print("===================================")
    print(f"{config.hotkey_main_mode} -> Ativar/desativar")
    print(f"{config.hotkey_side_mode} -> Ativar/desativar lateral")
    print(f"{config.hotkey_exit} -> Sair")
    print("A/D -> Alternancia automatica entre 0.5s e 1.0s")
    print("Clique -> CTRL por 0.8s")
    print("")

    # mouse dispara o efeito temporario sem controlar a alternancia.
    mouse_listener = mouse.Listener(
        on_click=watcher.handle_click,
    )
    hotkey_listener = HotkeyListener(
        config,
        watcher.toggle_main_mode,
        watcher.toggle_side_movement,
    )

    mouse_listener.start()
    hotkey_listener.start()

    try:
        hotkey_listener.wait()
    finally:
        # solta teclas injetadas antes de encerrar o processo.
        print("Finalizando...")
        watcher.shutdown()
        mouse_listener.stop()
        hotkey_listener.stop()


if __name__ == "__main__":
    main()
