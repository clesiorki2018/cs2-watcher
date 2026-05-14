from dataclasses import dataclass


@dataclass(frozen=True)
class WatcherConfig:
    """Configuração central de atalhos, teclas e tempos."""

    hotkey_main_mode: str = "f8"
    hotkey_side_mode: str = "f7"
    hotkey_exit: str = "esc"

    hold_key_forward: str = "w"
    hold_key_right: str = "d"
    hold_key_left: str = "a"
    effect_key: str = "ctrl"

    action_duration: float = 0.70
    click_debounce: float = 0.10
    hold_refresh_interval: float = 0.10

    @property
    def initial_side_hold_key(self) -> str:
        return self.hold_key_right
