# Copyright 2026 Clesiorki
# SPDX-License-Identifier: Apache-2.0

import keyboard

from cs2watcher.config import WatcherConfig


class BeepService:
    """Serviço de feedback sonoro via terminal bell."""

    def activated(self) -> None:
        print("\a", flush=True)

    def deactivated(self) -> None:
        print("\a\a", flush=True)


class KeyboardController:
    """Isola operações de teclado usadas pela lógica do watcher."""

    def __init__(self, config: WatcherConfig):
        self.config = config

    def press_forward(self) -> None:
        keyboard.press(self.config.hold_key_forward)

    def release_forward(self) -> None:
        keyboard.release(self.config.hold_key_forward)

    def press_effect(self) -> None:
        keyboard.press(self.config.effect_key)

    def release_effect(self) -> None:
        keyboard.release(self.config.effect_key)

    def press_key(self, key: str) -> None:
        keyboard.press(key)

    def release_side_keys(self) -> None:
        keyboard.release(self.config.hold_key_right)
        keyboard.release(self.config.hold_key_left)

    def release_all(self) -> None:
        self.release_effect()
        self.release_forward()
        self.release_side_keys()
