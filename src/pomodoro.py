import platform
import subprocess
import threading
import os
from textual.app import ComposeResult
from textual.widgets import Label, Button, Input, Switch
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

class PomodoroWidget(Vertical):
    """Widget para gerenciamento de tempo Pomodoro."""
    
    tempo_restante = reactive(25 * 60)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rodando = False
        self.atualizador = None
        self.modo = "Foco" # Pode ser "Foco" ou "Pausa"
        self.tempos = {"Foco": 25 * 60, "Pausa": 5 * 60}

    def compose(self) -> ComposeResult:
        yield Input(placeholder="O que você vai focar agora?", classes="cronometro_nome")
        
        with Vertical(classes="pomodoro_config_container"):
            with Horizontal(classes="pomodoro_config_tempos"):
                yield Label("Foco:", classes="label_pomodoro")
                yield Input(value="25", classes="input_pomodoro_foco", max_length=2)
                yield Label("Pausa:", classes="label_pomodoro")
                yield Input(value="05", classes="input_pomodoro_pausa", max_length=2)
            with Horizontal(classes="pomodoro_config_auto"):
                yield Label("Ciclos automáticos", classes="label_pomodoro")
                yield Switch(value=False, classes="switch_auto")
            
        yield Label("FOCO", classes="pomodoro_modo")
        yield Label("25:00", classes="tempo_display")
        
        with Horizontal(classes="cronometro_botoes"):
            yield Button("Iniciar", classes="iniciar_pausar", variant="success")
            yield Button("Alternar", classes="alternar", variant="warning")
            yield Button("Zerar", classes="zerar", variant="default")
            yield Button("Remover", classes="remover", variant="error")

    def watch_tempo_restante(self, tempo: int) -> None:
        minutos, segundos = divmod(tempo, 60)
        display = f"{int(minutos):02}:{int(segundos):02}"
        
        label_display = self.query_one(".tempo_display", Label)
        label_display.update(display)
        
        if tempo <= 0 and self.rodando:
            self.disparar_alarme()
            auto = self.query_one(".switch_auto", Switch).value
            self.alternar_modo(auto_start=auto) # Decide se continua sozinho

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.has_class("iniciar_pausar"):
            if self.rodando: self.pausar()
            else: self.iniciar()
        elif event.button.has_class("alternar"):
            self.alternar_modo(auto_start=False)
        elif event.button.has_class("zerar"):
            self.zerar()
        elif event.button.has_class("remover"):
            self.pausar()
            self.remove()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Aplica a máscara e atualiza os tempos do pomodoro simultaneamente."""
        if event.input.has_class("input_pomodoro_foco") or event.input.has_class("input_pomodoro_pausa"):
            numeros = "".join(filter(str.isdigit, event.value))[:2]
            
            if event.value != numeros:
                event.input.value = numeros
                event.input.cursor_position = len(numeros)
            
            self.atualizar_tempos()
            if not self.rodando:
                self.tempo_restante = self.tempos[self.modo]

    def iniciar(self) -> None:
        self.atualizar_tempos()
        if self.tempo_restante <= 0:
            self.tempo_restante = self.tempos[self.modo]
        if self.tempo_restante > 0:
            self.rodando = True
            self.atualizador = self.set_interval(1, self.atualizar_tempo)
            botao = self.query_one(".iniciar_pausar", Button)
            botao.label = "Pausar"
            botao.variant = "warning"

    def pausar(self) -> None:
        self.rodando = False
        if self.atualizador: self.atualizador.pause()
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Retomar"
        botao.variant = "success"

    def zerar(self) -> None:
        self.pausar()
        self.atualizar_tempos()
        self.tempo_restante = self.tempos[self.modo]
        self.query_one(".iniciar_pausar", Button).label = "Iniciar"

    def alternar_modo(self, auto_start=False) -> None:
        """Muda o modo. Inicia sozinho caso a chave de Auto esteja ligada."""
        self.pausar()
        self.modo = "Pausa" if self.modo == "Foco" else "Foco"
        self.atualizar_tempos()
        self.tempo_restante = self.tempos[self.modo]
        self.query_one(".pomodoro_modo", Label).update(self.modo.upper())
        self.query_one(".iniciar_pausar", Button).label = "Iniciar"
        if auto_start:
            self.iniciar()

    def atualizar_tempos(self) -> None:
        """Lê os valores digitados e os guarda em segundos."""
        try:
            f_str = self.query_one(".input_pomodoro_foco", Input).value or "0"
            p_str = self.query_one(".input_pomodoro_pausa", Input).value or "0"
            self.tempos["Foco"] = int(f_str) * 60
            self.tempos["Pausa"] = int(p_str) * 60
        except Exception: pass

    def atualizar_tempo(self) -> None:
        self.tempo_restante -= 1

    def disparar_alarme(self) -> None:
        mensagem = f"O tempo de {self.modo} acabou! Prepare-se."
        def notificar():
            sistema = platform.system()
            if sistema == "Windows":
                cmd = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;
                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument;
                $xml.LoadXml('<toast scenario="reminder"><visual><binding template="ToastGeneric"><text hint-maxLines="1">🍅 Pomodoro App</text><text>{mensagem}</text></binding></visual></toast>');
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Relógio TUI').Show([Windows.UI.Notifications.ToastNotification]::new($xml))
                """
                subprocess.run(["powershell", "-Command", cmd], creationflags=0x08000000)
                try:
                    import winsound
                    for _ in range(5):
                        winsound.Beep(2000, 500) # 5 bipes altos e agudos (500ms cada)
                except Exception: pass
            elif sistema == "Linux":
                try:
                    subprocess.run(["notify-send", "--urgency=critical", "Pomodoro (TUI)", mensagem])
                    subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"])
                except Exception: pass
        threading.Thread(target=notificar, daemon=True).start()