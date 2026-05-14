import threading
import time

import keyboard
from pynput import mouse


# ===========================================================
# HOTKEYS
# ===========================================================

HOTKEY_MAIN_MODE = "f8"
HOTKEY_SIDE_MODE = "f7"
HOTKEY_EXIT = "esc"


# ===========================================================
# TECLAS
# ===========================================================

HOLD_KEY_FORWARD = "w"

HOLD_KEY_RIGHT = "d"
HOLD_KEY_LEFT = "a"

EFFECT_KEY = "ctrl"

INITIAL_SIDE_HOLD_KEY = HOLD_KEY_RIGHT


# ===========================================================
# TEMPOS
# ===========================================================

ACTION_DURATION = 0.70          # CTRL fica pressionado por 0.7s
CLICK_DEBOUNCE = 0.10
HOLD_REFRESH_INTERVAL = 0.10    # reforça W + A/D a cada 0.1s


# ===========================================================
# BEEP
# ===========================================================

class BeepService:
    @staticmethod
    def activated():
        print("\a", flush=True)

    @staticmethod
    def deactivated():
        print("\a\a", flush=True)


# ===========================================================
# WATCHER
# ===========================================================

class AccessibilityWatcher:
    """
    F8:
        Ativa/desativa o modo principal.

    F7:
        Ativa/desativa o movimento lateral.

    Quando ativo e parado:
        - W fica pressionado.
        - A ou D fica pressionado se o movimento lateral estiver ativo.
        - Um watchdog reforça W + A/D periodicamente.

    A cada clique:
        - solta W;
        - solta A/D;
        - pressiona CTRL por 0.7 segundos;
        - durante esses 0.7s, W/A/D ficam soltos;
        - solta CTRL;
        - volta a pressionar W;
        - alterna o lateral:
            D -> A
            A -> D
    """

    def __init__(self):
        self.main_mode = False
        self.side_movement_enabled = True
        self.current_side_hold_key = None

        self.lock = threading.RLock()

        self.release_timer = None
        self.last_click_time = 0.0
        self.action_running = False

        self.stop_event = threading.Event()

        self.hold_refresh_thread = threading.Thread(
            target=self._hold_refresh_loop,
            daemon=True
        )
        self.hold_refresh_thread.start()

    # =======================================================
    # HOLD LATERAL
    # =======================================================

    def _release_side_hold_keys(self):
        """
        Solta A e D.

        Isso garante que nunca fiquem A e D pressionados ao mesmo tempo.
        """

        keyboard.release(HOLD_KEY_RIGHT)
        keyboard.release(HOLD_KEY_LEFT)
        self.current_side_hold_key = None

    def _press_side_hold_key(self, key):
        """
        Pressiona apenas uma tecla lateral por vez.
        """

        self._release_side_hold_keys()

        keyboard.press(key)
        self.current_side_hold_key = key

        print(f"HOLD lateral atual: [{key.upper()}]")

    def _get_next_side_key(self, previous_key):
        """
        Alterna a tecla lateral depois do efeito do CTRL.
        """

        if previous_key == HOLD_KEY_RIGHT:
            return HOLD_KEY_LEFT

        if previous_key == HOLD_KEY_LEFT:
            return HOLD_KEY_RIGHT

        return INITIAL_SIDE_HOLD_KEY

    # =======================================================
    # WATCHDOG DO HOLD
    # =======================================================

    def _hold_refresh_loop(self):
        """
        Reforça periodicamente W + A/D.

        Motivo:
        Alguns jogos/apps perdem o estado artificial de tecla pressionada
        após alguns segundos, mesmo rodando como root.

        Importante:
        Durante o efeito do clique, action_running fica True.
        Nesse período o watchdog NÃO pressiona W/A/D.
        """

        while not self.stop_event.is_set():
            with self.lock:
                if self.main_mode and not self.action_running:
                    keyboard.press(HOLD_KEY_FORWARD)

                    if (
                        self.side_movement_enabled
                        and self.current_side_hold_key is not None
                    ):
                        keyboard.press(self.current_side_hold_key)

            time.sleep(HOLD_REFRESH_INTERVAL)

    # =======================================================
    # TIMER
    # =======================================================

    def _cancel_release_timer(self):
        """
        Cancela o timer atual, se existir.
        """

        if self.release_timer is not None:
            self.release_timer.cancel()
            self.release_timer = None

    def _finish_click_effect(self, previous_side_key):
        """
        Finaliza o efeito do clique.

        Depois de 0.7s:
        - solta CTRL;
        - volta a pressionar W;
        - alterna e pressiona A ou D.
        """

        with self.lock:
            keyboard.release(EFFECT_KEY)

            if self.main_mode:
                keyboard.press(HOLD_KEY_FORWARD)

                if self.side_movement_enabled:
                    next_side_key = self._get_next_side_key(previous_side_key)
                    self._press_side_hold_key(next_side_key)
                else:
                    self._release_side_hold_keys()

            self.action_running = False
            self.release_timer = None

    # =======================================================
    # F8
    # =======================================================

    def toggle_main_mode(self):
        """
        Liga/desliga o modo principal.
        """

        with self.lock:
            self.main_mode = not self.main_mode

            if self.main_mode:
                print("Modo principal ativado")

                keyboard.press(HOLD_KEY_FORWARD)

                if self.side_movement_enabled:
                    self._press_side_hold_key(INITIAL_SIDE_HOLD_KEY)

                BeepService.activated()

            else:
                print("Modo principal desativado")

                self._cancel_release_timer()

                keyboard.release(EFFECT_KEY)
                keyboard.release(HOLD_KEY_FORWARD)
                self._release_side_hold_keys()

                self.action_running = False

                BeepService.deactivated()

    # =======================================================
    # F7
    # =======================================================

    def toggle_side_movement(self):
        """
        Liga/desliga apenas o movimento lateral A/D.
        """

        with self.lock:
            self.side_movement_enabled = not self.side_movement_enabled

            if self.side_movement_enabled:
                print("Movimento lateral ativado")

                if self.main_mode and not self.action_running:
                    side_key = self.current_side_hold_key or INITIAL_SIDE_HOLD_KEY
                    self._press_side_hold_key(side_key)

                BeepService.activated()

            else:
                print("Movimento lateral desativado")
                self._release_side_hold_keys()
                BeepService.deactivated()

    # =======================================================
    # CLIQUE DO MOUSE
    # =======================================================

    def handle_click(self, x, y, button, pressed):
        """
        Executado a cada clique do mouse.

        Durante o efeito:
        - W fica solto;
        - A/D ficam soltos;
        - somente CTRL fica pressionado por 0.7s.
        """

        if not pressed:
            return

        if not self.main_mode:
            return

        now = time.monotonic()

        with self.lock:
            if (now - self.last_click_time) < CLICK_DEBOUNCE:
                return

            self.last_click_time = now

            if self.action_running:
                return

            self.action_running = True

            self._cancel_release_timer()

            previous_side_key = self.current_side_hold_key

            keyboard.release(HOLD_KEY_FORWARD)
            self._release_side_hold_keys()

            keyboard.press(EFFECT_KEY)

            print("Clique: CTRL por 0.7s")

            self.release_timer = threading.Timer(
                ACTION_DURATION,
                self._finish_click_effect,
                args=(previous_side_key,)
            )

            self.release_timer.daemon = True
            self.release_timer.start()

    # =======================================================
    # FINALIZAÇÃO
    # =======================================================

    def shutdown(self):
        """
        Finaliza o programa soltando tudo com segurança.
        """

        with self.lock:
            self.stop_event.set()

            self._cancel_release_timer()

            keyboard.release(EFFECT_KEY)
            keyboard.release(HOLD_KEY_FORWARD)
            self._release_side_hold_keys()

            self.action_running = False


# ===========================================================
# MAIN
# ===========================================================

def main():
    watcher = AccessibilityWatcher()

    print("===================================")
    print(" Accessibility Watcher")
    print("===================================")
    print(f"{HOTKEY_MAIN_MODE} -> Ativar/desativar")
    print(f"{HOTKEY_SIDE_MODE} -> Ativar/desativar lateral")
    print(f"{HOTKEY_EXIT} -> Sair")
    print("")

    mouse_listener = mouse.Listener(
        on_click=watcher.handle_click
    )

    mouse_listener.start()

    keyboard.add_hotkey(
        HOTKEY_MAIN_MODE,
        watcher.toggle_main_mode
    )

    keyboard.add_hotkey(
        HOTKEY_SIDE_MODE,
        watcher.toggle_side_movement
    )

    try:
        keyboard.wait(HOTKEY_EXIT)

    finally:
        print("Finalizando...")
        watcher.shutdown()
        mouse_listener.stop()


if __name__ == "__main__":
    main()
