# Copyright 2026 Clesiorki
# SPDX-License-Identifier: Apache-2.0

import threading
import time
from random import uniform
from typing import Optional

from cs2watcher.config import WatcherConfig
from cs2watcher.io import BeepService, KeyboardController


class AccessibilityWatcher:
    """Coordena modo principal, movimento lateral e efeito de clique."""

    def __init__(
        self,
        config: WatcherConfig,
        keyboard_controller: KeyboardController,
        beep_service: BeepService,
    ) -> None:
        self.config = config
        self.keyboard = keyboard_controller
        self.beep = beep_service

        self.main_mode = False
        self.side_movement_enabled = True
        self.current_side_hold_key: Optional[str] = None

        # estado compartilhado fica protegido por lock reentrante.
        self.lock = threading.RLock()
        self.release_timer: Optional[threading.Timer] = None
        self.last_click_time = 0.0
        self.action_running = False
        self.stop_event = threading.Event()
        self.next_side_switch_time = 0.0

        self.hold_refresh_thread = threading.Thread(
            target=self._hold_refresh_loop,
            daemon=True,
        )
        self.hold_refresh_thread.start()

    @classmethod
    def build_default(cls) -> "AccessibilityWatcher":
        config = WatcherConfig.from_env()
        keyboard_controller = KeyboardController(config)

        return cls(config, keyboard_controller, BeepService())

    def toggle_main_mode(self) -> None:
        """F8 alterna o watcher completo."""

        with self.lock:
            self.main_mode = not self.main_mode

            if self.main_mode:
                self._activate_main_mode()
                return

            self._deactivate_main_mode()

    def toggle_side_movement(self) -> None:
        """F7 alterna apenas o hold lateral A/D."""

        with self.lock:
            self.side_movement_enabled = not self.side_movement_enabled

            if self.side_movement_enabled:
                self._enable_side_movement()
                return

            self._disable_side_movement()

    def handle_click(self, _x, _y, _button, pressed: bool) -> None:
        """Executa CTRL temporario para cada clique aceito."""

        if not pressed or not self.main_mode:
            return

        now = time.monotonic()

        with self.lock:
            if self._should_ignore_click(now):
                return

            self.last_click_time = now

            if self.action_running:
                return

            self._start_click_effect()

    def shutdown(self) -> None:
        """Para tarefas em segundo plano e solta todas as teclas."""

        with self.lock:
            self.stop_event.set()
            self._cancel_release_timer()
            self.keyboard.release_all()
            self.current_side_hold_key = None
            self.action_running = False

    def _activate_main_mode(self) -> None:
        print("Modo principal ativado")

        self._keep_forward_pressed()

        if self.side_movement_enabled:
            self._press_side_hold_key(self.config.initial_side_hold_key)
            self._schedule_next_side_switch()

        self.beep.activated()

    def _deactivate_main_mode(self) -> None:
        print("Modo principal desativado")

        self._cancel_release_timer()
        self.keyboard.release_all()
        self.current_side_hold_key = None
        self.action_running = False
        self.beep.deactivated()

    def _enable_side_movement(self) -> None:
        print("Movimento lateral ativado")

        if self.main_mode:
            side_key = self.current_side_hold_key or self.config.initial_side_hold_key
            self._press_side_hold_key(side_key)
            self._schedule_next_side_switch()

        self.beep.activated()

    def _disable_side_movement(self) -> None:
        print("Movimento lateral desativado")
        self._release_side_hold_keys()
        self._keep_forward_pressed()
        self.next_side_switch_time = 0.0
        self.beep.deactivated()

    def _start_click_effect(self) -> None:
        self.action_running = True
        self._cancel_release_timer()

        previous_side_key = self.current_side_hold_key

        self.keyboard.release_forward()
        self._release_side_hold_keys()
        self.keyboard.press_effect()

        print(f"Clique: CTRL por {self.config.action_duration:.2f}s")

        self.release_timer = threading.Timer(
            self.config.action_duration,
            self._finish_click_effect,
            args=(previous_side_key,),
        )
        self.release_timer.daemon = True
        self.release_timer.start()

    def _cancel_release_timer(self) -> None:
        if self.release_timer is None:
            return

        self.release_timer.cancel()
        self.release_timer = None

    def _finish_click_effect(self, previous_side_key: Optional[str]) -> None:
        with self.lock:
            self.keyboard.release_effect()

            self.action_running = False

            if self.main_mode:
                self._restore_side_movement(previous_side_key)
                self._keep_forward_pressed()

            self.release_timer = None

    def _restore_side_movement(self, previous_side_key: Optional[str]) -> None:
        if not self.side_movement_enabled:
            self._release_side_hold_keys()
            return

        next_side_key = self._get_next_side_key(previous_side_key)
        self._press_side_hold_key(next_side_key)
        self._schedule_next_side_switch()

    def _hold_refresh_loop(self) -> None:
        # alguns jogos perdem holds artificiais; o refresh mantem o estado.
        while not self.stop_event.is_set():
            with self.lock:
                if self.main_mode and not self.action_running:
                    self._refresh_side_hold()
                    self._switch_side_when_due()
                    self._keep_forward_pressed()

            time.sleep(self.config.hold_refresh_interval)

    def _keep_forward_pressed(self) -> None:
        # W e o hold base do modo principal e nunca depende da lateral.
        if self.main_mode and not self.action_running:
            self.keyboard.press_forward()

    def _refresh_side_hold(self) -> None:
        if not self.side_movement_enabled:
            return

        if self.current_side_hold_key is not None:
            self.keyboard.press_key(self.current_side_hold_key)

    def _press_side_hold_key(self, key: str) -> None:
        self._release_side_hold_keys()
        self.keyboard.press_key(key)
        self.current_side_hold_key = key
        self._keep_forward_pressed()

        print(f"HOLD lateral atual: [{key.upper()}]")

    def _release_side_hold_keys(self) -> None:
        self.keyboard.release_side_keys()
        self.current_side_hold_key = None

    def _get_next_side_key(self, previous_key: Optional[str]) -> str:
        if previous_key == self.config.hold_key_right:
            return self.config.hold_key_left

        if previous_key == self.config.hold_key_left:
            return self.config.hold_key_right

        return self.config.initial_side_hold_key

    def _switch_side_when_due(self) -> None:
        # alternancia automatica substitui a dependencia de clique.
        if not self.side_movement_enabled:
            return

        now = time.monotonic()

        if now < self.next_side_switch_time:
            return

        next_side_key = self._get_next_side_key(self.current_side_hold_key)
        self._press_side_hold_key(next_side_key)
        self._schedule_next_side_switch()

    def _schedule_next_side_switch(self) -> None:
        # intervalo variavel evita um padrao fixo entre A e D.
        min_interval = self.config.side_switch_min_interval
        max_interval = self.config.side_switch_max_interval

        if max_interval < min_interval:
            max_interval = min_interval

        self.next_side_switch_time = time.monotonic() + uniform(
            min_interval,
            max_interval,
        )

    def _should_ignore_click(self, now: float) -> bool:
        return (now - self.last_click_time) < self.config.click_debounce
