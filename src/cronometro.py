from time import monotonic
from textual.app import ComposeResult
from textual.widgets import Label, Button, Input
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive

class CronometroWidget(Vertical):
    """Widget personalizado para o Cronômetro."""
    
    # `reactive` avisa o Textual para atualizar a tela quando esta variável mudar
    tempo_decorrido = reactive(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inicio = 0.0
        self.rodando = False
        self.atualizador = None

    def compose(self) -> ComposeResult:
        """Interface do cronômetro."""
        yield Input(placeholder="Nome do Cronômetro", classes="cronometro_nome")
        yield Label("00:00:00.00", classes="tempo_display")
        with Horizontal(classes="cronometro_botoes"):
            yield Button("Iniciar", classes="iniciar_pausar", variant="success")
            yield Button("Volta", classes="volta", variant="default")
            yield Button("Zerar", classes="zerar", variant="default")
            yield Button("Remover", classes="remover", variant="error")
        yield VerticalScroll(classes="laps_container")

    def watch_tempo_decorrido(self, tempo: float) -> None:
        """Método chamado automaticamente quando `tempo_decorrido` muda."""
        minutos, segundos = divmod(tempo, 60)
        horas, minutos = divmod(minutos, 60)
        decimos = int((tempo - int(tempo)) * 100)
        
        # Formata o tempo e atualiza o display na tela
        display = f"{int(horas):02}:{int(minutos):02}:{int(segundos):02}.{decimos:02}"
        self.query_one(".tempo_display", Label).update(display)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques nos botões deste cronômetro específico."""
        # Verifica qual botão foi clicado através de sua classe
        if event.button.has_class("iniciar_pausar"):
            if self.rodando:
                self.pausar()
            else:
                self.iniciar()
        elif event.button.has_class("volta"):
            self.registrar_volta()
        elif event.button.has_class("zerar"):
            self.zerar()
        elif event.button.has_class("remover"):
            self.pausar() # Pausa o loop antes de deletar o widget da tela
            self.remove()

    def registrar_volta(self) -> None:
        """Registra o tempo atual como uma volta na lista."""
        if self.tempo_decorrido > 0:
            minutos, segundos = divmod(self.tempo_decorrido, 60)
            horas, minutos = divmod(minutos, 60)
            decimos = int((self.tempo_decorrido - int(self.tempo_decorrido)) * 100)
            display = f"{int(horas):02}:{int(minutos):02}:{int(segundos):02}.{decimos:02}"
            
            laps_container = self.query_one(".laps_container", VerticalScroll)
            numero_volta = len(laps_container.children) + 1
            laps_container.mount(Label(f"Volta {numero_volta} - {display}", classes="lap_label"))
            laps_container.scroll_end(animate=False)

    def iniciar(self) -> None:
        self.rodando = True
        self.inicio = monotonic() - self.tempo_decorrido
        self.atualizador = self.set_interval(1 / 60, self.atualizar_tempo)
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Pausar"
        botao.variant = "warning"
        display = self.query_one(".tempo_display", Label)
        display.remove_class("pausado")
        display.add_class("rodando")

    def pausar(self) -> None:
        self.rodando = False
        if self.atualizador:
            self.atualizador.pause()
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Retomar"
        botao.variant = "primary"
        display = self.query_one(".tempo_display", Label)
        display.remove_class("rodando")
        display.add_class("pausado")

    def zerar(self) -> None:
        self.pausar()
        self.tempo_decorrido = 0.0
        botao = self.query_one(".iniciar_pausar", Button)
        botao.label = "Iniciar"
        botao.variant = "success"
        display = self.query_one(".tempo_display", Label)
        display.remove_class("rodando")
        display.remove_class("pausado")
        laps = self.query_one(".laps_container", VerticalScroll)
        for lap in laps.children:
            lap.remove()

    def atualizar_tempo(self) -> None:
        self.tempo_decorrido = monotonic() - self.inicio