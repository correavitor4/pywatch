from time import monotonic
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Button
from textual.containers import Horizontal, Vertical
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
        yield Label("00:00:00.00", id="tempo_display")
        with Horizontal(id="cronometro_botoes"):
            yield Button("Iniciar", id="iniciar_pausar", variant="success")
            yield Button("Zerar", id="zerar", variant="error")

    def watch_tempo_decorrido(self, tempo: float) -> None:
        """Método chamado automaticamente quando `tempo_decorrido` muda."""
        minutos, segundos = divmod(tempo, 60)
        horas, minutos = divmod(minutos, 60)
        decimos = int((tempo - int(tempo)) * 100)
        
        # Formata o tempo e atualiza a Label na tela
        display = f"{int(horas):02}:{int(minutos):02}:{int(segundos):02}.{decimos:02}"
        self.query_one("#tempo_display", Label).update(display)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques nos botões Iniciar/Pausar e Zerar."""
        botao_id = event.button.id
        if botao_id == "iniciar_pausar":
            if self.rodando:
                self.pausar()
            else:
                self.iniciar()
        elif botao_id == "zerar":
            self.zerar()

    def iniciar(self) -> None:
        self.rodando = True
        self.inicio = monotonic() - self.tempo_decorrido
        # Cria um loop que executa a cada 1/60 segundos (60 FPS)
        self.atualizador = self.set_interval(1 / 60, self.atualizar_tempo)
        botao = self.query_one("#iniciar_pausar", Button)
        botao.label = "Pausar"
        botao.variant = "warning"

    def pausar(self) -> None:
        self.rodando = False
        if self.atualizador:
            self.atualizador.pause()
        botao = self.query_one("#iniciar_pausar", Button)
        botao.label = "Retomar"
        botao.variant = "success"

    def zerar(self) -> None:
        self.pausar()
        self.tempo_decorrido = 0.0
        botao = self.query_one("#iniciar_pausar", Button)
        botao.label = "Iniciar"
        botao.variant = "success"

    def atualizar_tempo(self) -> None:
        self.tempo_decorrido = monotonic() - self.inicio

class RelogioWindowsApp(App):
    """Clone do aplicativo de Relógio do Windows 11 em formato TUI."""

    # Título que aparecerá no cabeçalho
    TITLE = "Relógio do Sistema (TUI)"
    
    # CSS embutido básico para o layout
    CSS = """
    TabPane {
        align: center middle;
    }
    Label {
        color: $text-muted;
    }
    CronometroWidget {
        align: center middle;
    }
    #tempo_display {
        text-align: center;
        text-style: bold;
    }
    #cronometro_botoes {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    Button {
        margin: 0 2;
    }
    """

    # Atalhos de teclado que aparecerão no rodapé
    BINDINGS = [
        ("q", "quit", "Sair"),
        ("d", "toggle_dark", "Alternar Tema Escuro/Claro")
    ]

    def compose(self) -> ComposeResult:
        """Constrói a hierarquia da interface do usuário."""
        # Cabeçalho que já traz um relógio pequeno por padrão
        yield Header(show_clock=True)
        
        # Estrutura das 4 abas principais
        with TabbedContent(initial="aba_relogio_mundial"):
            with TabPane("Relógio Mundial", id="aba_relogio_mundial"):
                yield Label("A interface com fusos horários ficará aqui.")
                
            with TabPane("Alarmes", id="aba_alarmes"):
                yield Label("Lista de alarmes configuráveis ficará aqui.")
                
            with TabPane("Cronômetro", id="aba_cronometro"):
                yield CronometroWidget()
                
            with TabPane("Temporizador", id="aba_temporizador"):
                yield Label("A contagem regressiva ficará aqui.")
        
        yield Footer()

if __name__ == "__main__":
    app = RelogioWindowsApp()
    app.run()
