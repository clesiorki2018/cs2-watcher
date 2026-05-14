"""
Watcher de acessibilidade

Função:
- NUMPAD 3 ativa/desativa o sistema
- Quando ativo:
    clique do mouse pressiona 'a' ou 'd' aleatoriamente
- Emite beep indicando estado

Compatível com Linux Mint
"""

import random
import time
import threading
import os

from pynput import mouse
import keyboard


# -----------------------------------------------------------
# Serviço responsável apenas pelos sons
# -----------------------------------------------------------
class BeepService:

    @staticmethod
    def activated():
        print('\a', flush=True)

    @staticmethod
    def deactivated():
        print('\a\a', flush=True)


# -----------------------------------------------------------
# Serviço responsável por pressionar teclas aleatórias
# -----------------------------------------------------------
class RandomKeyPressService:

    def __init__(self):
        self.min_time = 0.1
        self.max_time = 0.2

    def press_random_key(self):

        key = random.choice(["a", "d"])
        duration = random.uniform(self.min_time, self.max_time)

        time.sleep(0.5)

        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)


# -----------------------------------------------------------
# Watcher principal
# -----------------------------------------------------------
class AccessibilityWatcher:

    def __init__(self):

        self.active = False
        self.lock = threading.Lock()

        self.key_service = RandomKeyPressService()

    def toggle(self):

        with self.lock:
            self.active = not self.active

            if self.active:
                print("Watcher ATIVADO")
                threading.Thread(target=BeepService.activated).start()
            else:
                print("Watcher DESATIVADO")
                threading.Thread(target=BeepService.deactivated).start()

    def handle_click(self, x, y, button, pressed):

        if pressed and self.active:
            threading.Thread(target=self.key_service.press_random_key).start()


# -----------------------------------------------------------
# Inicialização
# -----------------------------------------------------------
def main():

    watcher = AccessibilityWatcher()

    print("Pressione NUMPAD 3 para ativar/desativar")

    # Listener do mouse
    mouse_listener = mouse.Listener(
        on_click=watcher.handle_click
    )

    mouse_listener.start()

    # Hotkey confiável
    keyboard.add_hotkey("num 3", watcher.toggle)

    keyboard.wait()


if __name__ == "__main__":
    main()
