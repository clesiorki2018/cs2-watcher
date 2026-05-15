import os
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
    hotkey_debounce: float = 0.30

    @classmethod
    def from_env(cls) -> "WatcherConfig":
        """Cria configuracao permitindo sobrescrita por variaveis de ambiente."""

        return cls(
            hotkey_main_mode=_get_env_str("CS2_HOTKEY_MAIN_MODE", cls.hotkey_main_mode),
            hotkey_side_mode=_get_env_str("CS2_HOTKEY_SIDE_MODE", cls.hotkey_side_mode),
            hotkey_exit=_get_env_str("CS2_HOTKEY_EXIT", cls.hotkey_exit),
            hold_key_forward=_get_env_str("CS2_HOLD_KEY_FORWARD", cls.hold_key_forward),
            hold_key_right=_get_env_str("CS2_HOLD_KEY_RIGHT", cls.hold_key_right),
            hold_key_left=_get_env_str("CS2_HOLD_KEY_LEFT", cls.hold_key_left),
            effect_key=_get_env_str("CS2_EFFECT_KEY", cls.effect_key),
            action_duration=_get_env_float(
                "CS2_ACTION_DURATION",
                cls.action_duration,
            ),
            click_debounce=_get_env_float("CS2_CLICK_DEBOUNCE", cls.click_debounce),
            hold_refresh_interval=_get_env_float(
                "CS2_HOLD_REFRESH_INTERVAL",
                cls.hold_refresh_interval,
            ),
            hotkey_debounce=_get_env_float("CS2_HOTKEY_DEBOUNCE", cls.hotkey_debounce),
        )

    @property
    def initial_side_hold_key(self) -> str:
        return self.hold_key_right


def _get_env_str(name: str, default: str) -> str:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    return value


def _get_env_float(name: str, default: float) -> float:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    return float(value)
