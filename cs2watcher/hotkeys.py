# Copyright 2026 Clesiorki
# SPDX-License-Identifier: Apache-2.0

import threading
import time
from typing import Callable

from pynput import keyboard as pynput_keyboard

from cs2watcher.config import WatcherConfig


class HotkeyListener:
    """Escuta hotkeys físicas sem misturar com a injeção de teclas."""

    def __init__(
        self,
        config: WatcherConfig,
        on_main_mode: Callable[[], None],
        on_side_movement: Callable[[], None],
    ) -> None:
        self.config = config
        self.on_main_mode = on_main_mode
        self.on_side_movement = on_side_movement

        self.stop_event = threading.Event()
        self.last_trigger_time: dict[str, float] = {}

        # pynput usa objetos Key para teclas especiais como F8 e ESC.
        self.main_mode_key = self._key_from_name(config.hotkey_main_mode)
        self.side_movement_key = self._key_from_name(config.hotkey_side_mode)
        self.exit_key = self._key_from_name(config.hotkey_exit)

        self.listener = pynput_keyboard.Listener(on_press=self._handle_press)

    def start(self) -> None:
        self.listener.start()

    def wait(self) -> None:
        self.stop_event.wait()

    def stop(self) -> None:
        self.stop_event.set()
        self.listener.stop()

    def _handle_press(self, key) -> bool | None:
        if key == self.exit_key:
            self.stop_event.set()
            return False

        if key == self.main_mode_key and self._can_trigger("main"):
            self.on_main_mode()
            return None

        if key == self.side_movement_key and self._can_trigger("side"):
            self.on_side_movement()
            return None

        return None

    def _can_trigger(self, action: str) -> bool:
        now = time.monotonic()
        last_time = self.last_trigger_time.get(action, 0.0)

        # debounce evita repeticao quando o sistema segura a hotkey.
        if (now - last_time) < self.config.hotkey_debounce:
            return False

        self.last_trigger_time[action] = now
        return True

    def _key_from_name(self, name: str):
        return getattr(pynput_keyboard.Key, name.lower())
