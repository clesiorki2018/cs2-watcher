<!--
Copyright 2026 Clesiorki
SPDX-License-Identifier: Apache-2.0
-->

# Prompt PlantUML do projeto CS2 Watcher

Use este prompt para gerar diagramas PlantUML fieis ao projeto.

```text
Voce e um arquiteto de software senior. Analise o projeto Python "CS2 Watcher" e gere diagramas PlantUML claros, objetivos e consistentes com Clean Architecture, SOLID e Clean Code.

Contexto do projeto:
- O projeto automatiza acessibilidade de teclado/mouse para Counter-Strike 2.
- O ponto de entrada e `watcher.py`.
- `watcher.py` cria um `AccessibilityWatcher`, um listener de mouse e um `HotkeyListener`.
- `AccessibilityWatcher` coordena o modo principal, a alternancia automatica de A/D e o efeito de clique.
- `WatcherConfig` centraliza hotkeys, teclas e tempos.
- `HotkeyListener` escuta teclas fisicas com `pynput.keyboard.Listener`.
- `KeyboardController` isola chamadas da biblioteca externa `keyboard`.
- `BeepService` fornece feedback sonoro via terminal bell.
- O script `cs2_watcher.sh` carrega `.env`, resolve caminhos locais e executa `watcher.py` com sudo.

Arquivos e responsabilidades:

1. `watcher.py`
- Funcao `main()`.
- Constroi `AccessibilityWatcher.build_default()`.
- Exibe as hotkeys configuradas.
- Cria `mouse.Listener(on_click=watcher.handle_click)`.
- Cria `HotkeyListener(config, watcher.toggle_main_mode, watcher.toggle_side_movement)`.
- Inicia os listeners.
- Aguarda `hotkey_listener.wait()`.
- No `finally`, chama `watcher.shutdown()` e para o listener de hotkeys.

2. `cs2watcher/config.py`
- Classe `WatcherConfig`, dataclass congelada.
- Campos:
  - `hotkey_main_mode = "f8"`
  - `hotkey_side_mode = "f7"`
  - `hotkey_exit = "esc"`
  - `hold_key_forward = "w"`
  - `hold_key_right = "d"`
  - `hold_key_left = "a"`
  - `effect_key = "ctrl"`
  - `action_duration = 0.80`
  - `click_debounce = 0.10`
  - `hold_refresh_interval = 0.10`
  - `hotkey_debounce = 0.30`
  - `side_switch_min_interval = 0.50`
  - `side_switch_max_interval = 1.00`
- Propriedade `initial_side_hold_key`, que retorna `hold_key_right`.

3. `cs2watcher/io.py`
- Classe `BeepService`.
  - `activated()` imprime um terminal bell.
  - `deactivated()` imprime dois terminal bells.
- Classe `KeyboardController`.
  - Recebe `WatcherConfig`.
  - `press_forward()` pressiona `hold_key_forward`.
  - `release_forward()` solta `hold_key_forward`.
  - `press_effect()` pressiona `effect_key`.
  - `release_effect()` solta `effect_key`.
  - `press_key(key)` pressiona uma tecla generica.
  - `release_side_keys()` solta `hold_key_right` e `hold_key_left`.
  - `release_all()` solta frente e laterais.

4. `cs2watcher/hotkeys.py`
- Classe `HotkeyListener`.
- Recebe `WatcherConfig`, callback `on_main_mode` e callback `on_side_movement`.
- Usa `pynput.keyboard.Listener(on_press=self._handle_press)`.
- Mantem `stop_event` e `last_trigger_time`.
- `_can_trigger(action)` aplica debounce por acao usando `time.monotonic()`.

5. `cs2watcher/watcher.py`
- Classe `AccessibilityWatcher`.
- Estado:
  - `main_mode`
  - `side_movement_enabled`
  - `current_side_hold_key`
  - `release_timer`
  - `last_click_time`
  - `action_running`
  - `stop_event`
  - `lock`
  - `next_side_switch_time`
  - `forward_hold_thread`
  - `side_movement_thread`
- `_forward_hold_loop()` mantem W pressionado enquanto o modo principal esta ativo e CTRL nao esta ativo.
- `_side_movement_loop()` reaplica a lateral atual e chama `_switch_side_when_due()`.
- `_switch_side_when_due()` alterna entre A e D quando o intervalo vence.
- `_schedule_next_side_switch()` agenda o proximo intervalo com `random.uniform(0.5, 1.0)`.
- `handle_click()` solta W/A/D, pressiona CTRL por 0.8s e restaura o movimento.

Gere obrigatoriamente:

1. Um diagrama de componentes PlantUML.
2. Um diagrama de classes PlantUML.
3. Um diagrama de sequencia PlantUML para ativar F8, alternar A/D automaticamente e executar o efeito de clique.
4. Um diagrama de estados PlantUML para `AccessibilityWatcher` contendo `Desativado`, `ModoPrincipalAtivo`, `MovimentoLateralAtivo`, `MovimentoLateralDesativado`, `EfeitoCliqueEmExecucao` e transicoes por F8, F7, intervalo vencido, clique aceito, timer finalizado e shutdown.

Regras de saida:
- Responda apenas com codigo PlantUML em blocos separados.
- Cada bloco deve iniciar com `@startuml` e terminar com `@enduml`.
- Use nomes em portugues, mas preserve nomes reais de classes e metodos.
- Evite inventar classes que nao existem.
- Quando representar bibliotecas externas, use estereotipo `<<external>>`.
- Use notas curtas somente onde ajudarem a explicar concorrencia, debounce, timer ou alternancia.
```
