from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Button
from textual.containers import VerticalScroll

from cronometro import CronometroWidget
from temporizador import TemporizadorWidget
from relogio_mundial import RelogioMundialWidget, FusoHorarioWidget
from alarme import AlarmeWidget

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
    #aba_cronometro, #aba_relogio_mundial, #aba_alarmes {
        align: center top;
    }
    CronometroWidget, TemporizadorWidget, FusoHorarioWidget, AlarmeWidget {
        align: center middle;
        height: auto;
        min-height: 10;
        width: 100%;
        margin: 0;
        border: round $primary-muted; /* Borda mais suave e elegante */
        padding: 1 2;
        background: $panel; /* Fundo que simula a elevação do Windows 11 */
    }
    .cronometro_nome {
        width: 100%;
        border: none;
        background: transparent;
        text-align: center;
    }
    .cronometro_nome:focus {
        border: none;
    }
    .tempo_display {
        text-align: center; /* Alinha os dígitos horizontalmente ao centro */
        text-style: bold;
        margin-bottom: 1;
    }
    .tempo_display.rodando {
        color: $success; /* Fica verde quando está em contagem */
    }
    .tempo_display.pausado {
        color: $warning; /* Fica amarelo quando pausado */
    }
    .input_tempo {
        width: 100%;
        text-align: center;
        text-style: bold;
        border: none;
        background: transparent;
        margin-bottom: 1;
    }
    .input_tempo:focus {
        border: none;
        background: $boost; /* Leve destaque quando estiver digitando */
    }
    .cronometro_botoes {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    .laps_container {
        height: auto;
        max-height: 5; /* Limita a altura da lista de voltas visíveis */
        width: 100%;
        margin-top: 1;
    }
    .lap_label {
        width: 100%;
        text-align: center;
        color: $text-muted;
    }
    RelogioMundialWidget {
        align: center middle;
        width: auto;
        height: auto;
        margin-bottom: 2; /* Espaço entre o relógio principal e os outros cartões */
    }
    #hora_atual {
        color: $primary;
    }
    #data_atual {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    .fuso_header {
        width: 100%;
        height: auto;
        align: center middle;
    }
    .select_fuso {
        width: 1fr;
    }
    .remover_fuso {
        min-width: 5;
        margin-left: 1;
    }
    .fuso_hora {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-top: 1;
    }
    .fuso_data {
        text-align: center;
        color: $text-muted;
    }
    .alarme_header {
        width: 100%;
        height: auto;
        align: center middle;
        margin-bottom: 1;
    }
    .input_alarme {
        width: 12;
        text-align: center;
        text-style: bold;
        border: none;
        background: transparent;
    }
    .input_alarme:focus {
        border: none;
        background: $boost;
    }
    AlarmeWidget.tocando {
        border: round $error; /* Borda fica em destaque vermelho quando toca */
        background: $error 15%;
    }
    #container_cronometros, #container_temporizadores, #container_fusos, #container_alarmes {
        width: 100%;
        height: 1fr;
        layout: grid;
        grid-size: 2; /* Cria 2 colunas, forçando o 3º item para a linha seguinte */
        grid-rows: auto; /* Permite que as linhas usem sua altura real, ativando o scroll */
        grid-gutter: 1 2; /* Adiciona espaçamento vertical e horizontal entre os cartões */
    }
    #btn_add_cronometro, #btn_add_temporizador, #btn_add_fuso, #btn_add_alarme {
        margin: 1;
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
                yield RelogioMundialWidget()
                yield Button("+ Adicionar Fuso Horário", id="btn_add_fuso", variant="primary")
                with VerticalScroll(id="container_fusos"):
                    pass
                
            with TabPane("Alarmes", id="aba_alarmes"):
                yield Button("+ Adicionar Alarme", id="btn_add_alarme", variant="primary")
                with VerticalScroll(id="container_alarmes"):
                    yield AlarmeWidget()
                
            with TabPane("Cronômetro", id="aba_cronometro"):
                yield Button("+ Adicionar Cronômetro", id="btn_add_cronometro", variant="primary")
                with VerticalScroll(id="container_cronometros"):
                    yield CronometroWidget()
                
            with TabPane("Temporizador", id="aba_temporizador"):
                yield Button("+ Adicionar Temporizador", id="btn_add_temporizador", variant="primary")
                with VerticalScroll(id="container_temporizadores"):
                    yield TemporizadorWidget()
        
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Detecta o botão de adicionar e anexa um novo widget de cronômetro."""
        if event.button.id == "btn_add_cronometro":
            container = self.query_one("#container_cronometros", VerticalScroll)
            container.mount(CronometroWidget())
            container.scroll_end(animate=False)
        elif event.button.id == "btn_add_temporizador":
            container = self.query_one("#container_temporizadores", VerticalScroll)
            container.mount(TemporizadorWidget())
            container.scroll_end(animate=False)
        elif event.button.id == "btn_add_fuso":
            container = self.query_one("#container_fusos", VerticalScroll)
            container.mount(FusoHorarioWidget())
            container.scroll_end(animate=False)
        elif event.button.id == "btn_add_alarme":
            container = self.query_one("#container_alarmes", VerticalScroll)
            container.mount(AlarmeWidget())
            container.scroll_end(animate=False)

if __name__ == "__main__":
    app = RelogioWindowsApp()
    app.run()
