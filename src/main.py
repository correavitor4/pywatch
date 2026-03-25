from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Button
from textual.containers import VerticalScroll

from cronometro import CronometroWidget

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
    #aba_cronometro {
        align: center top;
    }
    CronometroWidget {
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
    #container_cronometros {
        width: 100%;
        height: 1fr;
        layout: grid;
        grid-size: 2; /* Cria 2 colunas, forçando o 3º item para a linha seguinte */
        grid-rows: auto; /* Permite que as linhas usem sua altura real, ativando o scroll */
        grid-gutter: 1 2; /* Adiciona espaçamento vertical e horizontal entre os cartões */
    }
    #btn_add_cronometro {
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
                yield Label("A interface com fusos horários ficará aqui.")
                
            with TabPane("Alarmes", id="aba_alarmes"):
                yield Label("Lista de alarmes configuráveis ficará aqui.")
                
            with TabPane("Cronômetro", id="aba_cronometro"):
                yield Button("+ Adicionar Cronômetro", id="btn_add_cronometro", variant="primary")
                with VerticalScroll(id="container_cronometros"):
                    yield CronometroWidget()
                
            with TabPane("Temporizador", id="aba_temporizador"):
                yield Label("A contagem regressiva ficará aqui.")
        
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Detecta o botão de adicionar e anexa um novo widget de cronômetro."""
        if event.button.id == "btn_add_cronometro":
            container = self.query_one("#container_cronometros", VerticalScroll)
            container.mount(CronometroWidget())
            container.scroll_end(animate=False)

if __name__ == "__main__":
    app = RelogioWindowsApp()
    app.run()
