import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CalculadoraRetorno:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Retorno Total de Ações")
        self.root.state('zoomed')  # Abre a janela maximizada

        self.canvas = None
        self._criar_widgets()

    def _criar_widgets(self):
        # Frame para os controles
        frame_controles = tk.Frame(self.root)
        frame_controles.pack(pady=10)

        tk.Label(frame_controles, text="Código do Ativo:", font=('Arial', 12)).grid(row=0, column=0, padx=10)
        self.ticker_entry = tk.Entry(frame_controles, width=30, font=('Arial', 12))
        self.ticker_entry.grid(row=0, column=1, padx=10)

        tk.Label(frame_controles, text="Período:", font=('Arial', 12)).grid(row=1, column=0, padx=10)
        self.periodo_combobox = ttk.Combobox(
            frame_controles,
            values=['1d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'],
            state="readonly",
            font=('Arial', 12)
        )
        self.periodo_combobox.set('1y')  # Valor padrão
        self.periodo_combobox.grid(row=1, column=1, padx=10)

        tk.Button(frame_controles, text="Calcular Retorno Total", command=self._atualizar_interface, font=('Arial', 12)).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(frame_controles, text="Resetar", command=self._resetar_interface, font=('Arial', 12)).grid(row=3, column=0, columnspan=2, pady=10)

        # Frame para os resultados
        self.frame_resultados = tk.Frame(self.root)
        self.frame_resultados.pack(pady=10, fill=tk.BOTH, expand=True)

    def _obter_historico_dividendos(self, ticker, periodo):
        ativo = yf.Ticker(ticker)
        historico = ativo.history(period=periodo)
        dividendos = ativo.dividends

        if historico.empty:
            raise ValueError("Histórico vazio ou não encontrado.")
        return historico, dividendos

    def _calcular_metricas(self, historico, dividendos):
        preco_inicial = historico['Close'].iloc[0]
        preco_final = historico['Close'].iloc[-1]
        dividendos_periodo = dividendos.sum()
        
        # Dividendos dos últimos 4 trimestres
        dividendos_trimestrais = dividendos.resample('QE').sum()
        dividendos_ultimos_4_trimestres = dividendos_trimestrais.tail(4).sum()

        # Preço da ação no final do último ano
        preco_final_ano = historico['Close'].resample('YE').last().iloc[-1]

        retorno_acao = ((preco_final - preco_inicial) / preco_inicial) * 100
        retorno_total = ((preco_final - preco_inicial + dividendos_periodo) / preco_inicial) * 100
        dividend_on_cost = (dividendos_periodo / preco_inicial) * 100
        doc_ultimo_ano = (dividendos_ultimos_4_trimestres / preco_inicial) * 100
        dividend_yield = (dividendos_ultimos_4_trimestres / preco_final_ano) * 100 if preco_final_ano != 0 else 0

        return {
            "Preço Inicial": f'{preco_inicial:.2f}',
            "Preço Final": f'{preco_final:.2f}',
            "Dividendo do Último Ano": f'{dividendos_ultimos_4_trimestres:.2f}',
            "Dividend Yield Último Ano": f'{dividend_yield:.2f}%',
            "Dividendos Totais": f'{dividendos_periodo:.2f}',
            "Dividend on Cost": f'{dividend_on_cost:.2f}%',
            "DoC Último Ano": f'{doc_ultimo_ano:.2f}%',
            "Retorno Total": f'{retorno_total:.2f}%',
            "Retorno Apenas da Ação": f'{retorno_acao:.2f}%'
        }, historico, dividendos

    def _calcular_retorno_total(self, ticker, periodo):
        try:
            historico, dividendos = self._obter_historico_dividendos(ticker, periodo)
            metricas, historico, dividendos = self._calcular_metricas(historico, dividendos)

            return metricas, historico, dividendos

        except ValueError as e:
            return {"Erro": str(e)}, None, None

    def _plotar_graficos(self, historico, dividendos):
        historico_trimestral = historico['Close'].resample('QE').last()
        dividendos_trimestrais = dividendos.resample('QE').sum().fillna(0)

        preco_percentual = (historico_trimestral / historico_trimestral.iloc[0] - 1) * 100
        preco_com_dividendos = historico_trimestral + dividendos_trimestrais.cumsum()
        preco_com_dividendos_percentual = (preco_com_dividendos / historico_trimestral.iloc[0] - 1) * 100

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(preco_percentual.index, preco_percentual.values, color='blue', label='Variação Percentual do Preço da Ação')
        ax.plot(preco_com_dividendos_percentual.index, preco_com_dividendos_percentual.values, color='green', label='Variação Percentual com Dividendos Reinvestidos')

        ax.set_xlabel('Data', fontsize=14)
        ax.set_ylabel('Variação Percentual (%)', fontsize=14)
        ax.set_title('Variação Percentual do Preço da Ação e Retorno Total com Dividendos Reinvestidos', fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(True)

        # Adicionar anotações ao lado direito das linhas (somente último ponto)
        self._anotar_grafico(ax, preco_percentual, 'blue')
        self._anotar_grafico(ax, preco_com_dividendos_percentual, 'green')

        self._exibir_grafico(fig)

    def _anotar_grafico(self, ax, dados, cor):
        ax.annotate(
            f'{dados.values[-1]:.2f}%', 
            xy=(dados.index[-1], dados.values[-1]), 
            xytext=(10, 0), 
            textcoords='offset points', 
            color=cor,
            fontsize=12
        )

    def _exibir_grafico(self, fig):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _atualizar_interface(self):
        ticker = self.ticker_entry.get().strip().upper()
        periodo = self.periodo_combobox.get().strip().lower()

        if not ticker or not periodo:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")
            return

        resultado, historico, dividendos = self._calcular_retorno_total(ticker, periodo)

        if historico is not None and dividendos is not None:
            # Limpar frame de resultados
            self._limpar_resultados()

            # Exibir resultados em colunas
            colunas = [
                ["Preço Inicial", "Preço Final"],
                ["Dividendo do Último Ano", "Dividend Yield Último Ano", "Dividendos Totais", "Dividend on Cost", "DoC Último Ano"],
                ["Retorno Total", "Retorno Apenas da Ação"]
            ]

            for i, coluna in enumerate(colunas):
                for j, item in enumerate(coluna):
                    label_nome = tk.Label(self.frame_resultados, text=item, font=('Arial', 12, 'bold'))
                    label_nome.grid(row=j, column=i*2, padx=10, pady=5, sticky='nsew')
                    valor = tk.Label(self.frame_resultados, text=resultado.get(item, ''), font=('Arial', 12))
                    valor.grid(row=j, column=i*2+1, padx=10, pady=5, sticky='nsew')

                self.frame_resultados.grid_columnconfigure(i*2, weight=1)
                self.frame_resultados.grid_columnconfigure(i*2+1, weight=1)
                self.frame_resultados.grid_rowconfigure(len(coluna) - 1, weight=1)

            # Gerar o gráfico automaticamente após atualizar a interface
            self._plotar_graficos(historico, dividendos)

    def _resetar_interface(self):
        self.ticker_entry.delete(0, tk.END)
        self.periodo_combobox.set('1y')
        self._limpar_resultados()
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

    def _limpar_resultados(self):
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraRetorno(root)
    root.mainloop()
