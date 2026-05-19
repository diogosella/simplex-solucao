import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from simplex import resolver

MATERIAS = ["Cobre", "Zinco", "Chumbo"]
LIMITES = [16, 11, 15]
COMP_A = [2, 1, 1]
COMP_B = [1, 2, 3]
PRECO_A_DEFAULT = 30
PRECO_B_DEFAULT = 50

def resolver_otimo(preco_a, preco_b):
    c = [preco_a, preco_b]
    A_ub = [[COMP_A[i], COMP_B[i]] for i in range(3)]
    b_ub = LIMITES

    saida = resolver("max", c, A_ub, b_ub)
    if saida is None:
        return None

    x, z = saida
    return {
        "x1": float(x[0]),
        "x2": float(x[1]),
        "Z": z,
    }

class PlanejadorLigasApp:

    def __init__(self, root):
        self.root = root
        root.title("Planejador de Produção - Fábrica de Ligas Metálicas")
        root.geometry("980x720")
        root.minsize(900, 650)

        self.var_preco_a = tk.StringVar(value=str(PRECO_A_DEFAULT))
        self.var_preco_b = tk.StringVar(value=str(PRECO_B_DEFAULT))
        self.var_qtd_a = tk.StringVar(value="0")
        self.var_qtd_b = tk.StringVar(value="0")

        self._construir_ui()

    def _construir_ui(self):
        titulo = ttk.Label(self.root,
                           text="Planejador de Produção - Fábrica de Ligas Metálicas",
                           font=("TkDefaultFont", 13, "bold"))
        titulo.pack(pady=(10, 4))
        subt = ttk.Label(self.root,
                         text="Avalia se o plano de produção proposto compensa, "
                              "comparando-o com o ótimo via Simplex",
                         foreground="gray")
        subt.pack(pady=(0, 8))

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=4)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        col_esq = ttk.Frame(main)
        col_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        col_dir = ttk.Frame(main)
        col_dir.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        frm_mp = ttk.LabelFrame(col_esq, text="Matérias-primas disponíveis (estoque fixo)",
                                padding=8)
        frm_mp.pack(fill="x", pady=(0, 6))
        for i, mat in enumerate(MATERIAS):
            ttk.Label(frm_mp, text=f"{mat}:").grid(row=i, column=0, sticky="w", padx=4)
            ttk.Label(frm_mp, text=f"{LIMITES[i]} unidades",
                      font=("TkDefaultFont", 10, "bold")
                      ).grid(row=i, column=1, sticky="w", padx=4)

        frm_comp = ttk.LabelFrame(col_esq, text="Composição das ligas (fixa)", padding=8)
        frm_comp.pack(fill="x", pady=6)
        ttk.Label(frm_comp, text="").grid(row=0, column=0)
        ttk.Label(frm_comp, text="Liga A", font=("TkDefaultFont", 10, "bold")
                  ).grid(row=0, column=1, padx=10)
        ttk.Label(frm_comp, text="Liga B", font=("TkDefaultFont", 10, "bold")
                  ).grid(row=0, column=2, padx=10)
        for i, mat in enumerate(MATERIAS):
            ttk.Label(frm_comp, text=mat).grid(row=1 + i, column=0, sticky="w", padx=4)
            ttk.Label(frm_comp, text=str(COMP_A[i])).grid(row=1 + i, column=1)
            ttk.Label(frm_comp, text=str(COMP_B[i])).grid(row=1 + i, column=2)

        frm_pre = ttk.LabelFrame(col_esq, text="Preços de venda (cenário - editável)",
                                 padding=8)
        frm_pre.pack(fill="x", pady=6)
        ttk.Label(frm_pre, text="Liga A: R$").grid(row=0, column=0, sticky="e", padx=4)
        ttk.Entry(frm_pre, textvariable=self.var_preco_a, width=10, justify="center"
                  ).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(frm_pre, text="Liga B: R$").grid(row=0, column=2, sticky="e", padx=(20, 4))
        ttk.Entry(frm_pre, textvariable=self.var_preco_b, width=10, justify="center"
                  ).grid(row=0, column=3, padx=4, pady=2)

        frm_pl = ttk.LabelFrame(col_esq, text="Plano de produção proposto", padding=8)
        frm_pl.pack(fill="x", pady=6)
        ttk.Label(frm_pl, text="Quantidade de Liga A:").grid(row=0, column=0,
                                                              sticky="e", padx=4, pady=4)
        ttk.Entry(frm_pl, textvariable=self.var_qtd_a, width=10, justify="center"
                  ).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(frm_pl, text="Quantidade de Liga B:").grid(row=1, column=0,
                                                              sticky="e", padx=4, pady=4)
        ttk.Entry(frm_pl, textvariable=self.var_qtd_b, width=10, justify="center"
                  ).grid(row=1, column=1, padx=4, pady=4)

        frm_btn = ttk.Frame(col_esq)
        frm_btn.pack(fill="x", pady=(8, 0))
        ttk.Button(frm_btn, text="Avaliar plano",
                   command=self._avaliar).pack(side="left", padx=4)
        ttk.Button(frm_btn, text="Carregar plano ótimo",
                   command=self._carregar_otimo).pack(side="left", padx=4)

        frm_res = ttk.LabelFrame(col_dir, text="Avaliação do plano", padding=8)
        frm_res.pack(fill="both", expand=True)
        self.txt_resultado = scrolledtext.ScrolledText(frm_res, wrap="word",
                                                      font=("Consolas", 10), height=30)
        self.txt_resultado.pack(fill="both", expand=True)
        self.txt_resultado.tag_configure("titulo", font=("TkDefaultFont", 11, "bold"))
        self.txt_resultado.tag_configure("ok", foreground="#0a7a2e",
                                         font=("TkDefaultFont", 10, "bold"))
        self.txt_resultado.tag_configure("erro", foreground="#b00020",
                                         font=("TkDefaultFont", 10, "bold"))
        self.txt_resultado.tag_configure("aviso", foreground="#b07a00",
                                         font=("TkDefaultFont", 10, "bold"))
        self._escrever("Digite a quantidade desejada de cada liga "
                       "e clique em 'Avaliar plano'.\n", "")

    def _escrever(self, texto, tag=""):
        if tag:
            self.txt_resultado.insert("end", texto, tag)
        else:
            self.txt_resultado.insert("end", texto)
        self.txt_resultado.see("end")

    def _limpar_resultado(self):
        self.txt_resultado.delete("1.0", "end")

    def _ler_float(self, valor, nome):
        try:
            return float(str(valor).replace(",", "."))
        except ValueError:
            raise ValueError(f"Valor inválido em '{nome}': '{valor}'.")

    def _avaliar(self):
        self._limpar_resultado()
        try:
            preco_a = self._ler_float(self.var_preco_a.get(), "Preço Liga A")
            preco_b = self._ler_float(self.var_preco_b.get(), "Preço Liga B")
            qa = self._ler_float(self.var_qtd_a.get(), "Quantidade Liga A")
            qb = self._ler_float(self.var_qtd_b.get(), "Quantidade Liga B")
        except ValueError as e:
            messagebox.showerror("Entrada inválida", str(e))
            return

        if qa < 0 or qb < 0:
            messagebox.showerror("Entrada inválida",
                                 "As quantidades de produção não podem ser negativas.")
            return
        if preco_a < 0 or preco_b < 0:
            messagebox.showerror("Entrada inválida",
                                 "Os preços não podem ser negativos.")
            return

        if qa != int(qa) or qb != int(qb):
            messagebox.showwarning(
                "Atenção - frações de liga",
                "O enunciado diz que frações de liga metálica não podem ser "
                "consideradas. Os valores serão avaliados mesmo assim, mas "
                "considere usar números inteiros.")

        consumo = [COMP_A[i] * qa + COMP_B[i] * qb for i in range(3)]
        viavel = all(consumo[i] <= LIMITES[i] + 1e-9 for i in range(3))

        receita_plano = preco_a * qa + preco_b * qb

        otimo = resolver_otimo(preco_a, preco_b)

        self._escrever("CENÁRIO AVALIADO\n", "titulo")
        self._escrever(f"  Preço Liga A: R$ {preco_a:.2f}    "
                       f"Preço Liga B: R$ {preco_b:.2f}\n")
        self._escrever(f"  Plano proposto: produzir {qa:g} de Liga A "
                       f"e {qb:g} de Liga B\n\n")

        self._escrever("CONSUMO DE MATÉRIA-PRIMA\n", "titulo")
        for i, mat in enumerate(MATERIAS):
            cons = consumo[i]
            lim = LIMITES[i]
            sobra = lim - cons
            marca = "OK" if cons <= lim + 1e-9 else "EXCEDIDO"
            tag = "ok" if marca == "OK" else "erro"
            self._escrever(f"  {mat:8s} {cons:6.2f} / {lim:>2}   ")
            if sobra >= 0:
                self._escrever(f"(sobra {sobra:.2f})  ")
            else:
                self._escrever(f"(falta {-sobra:.2f})  ")
            self._escrever(f"[{marca}]\n", tag)
        self._escrever("\n")

        if not viavel:
            self._escrever("STATUS: PLANO INVIÁVEL\n", "erro")
            self._escrever("O plano excede o estoque de pelo menos uma matéria-prima. "
                           "Reduza a quantidade de produção.\n\n")
        else:
            self._escrever("STATUS: PLANO VIÁVEL\n", "ok")
            self._escrever("Todas as restrições de matéria-prima foram respeitadas.\n\n")

        self._escrever("ANÁLISE FINANCEIRA\n", "titulo")
        self._escrever(f"  Receita do seu plano:  R$ {receita_plano:8.2f}\n")

        if otimo is None:
            self._escrever("  (não foi possível calcular o ótimo)\n", "aviso")
            return

        self._escrever(f"  Receita ótima possível: R$ {otimo['Z']:8.2f}   "
                       f"(produzindo {otimo['x1']:.2f} de A e {otimo['x2']:.2f} de B)\n")

        diferenca = otimo["Z"] - receita_plano
        if otimo["Z"] > 1e-9:
            pct = 100 * receita_plano / otimo["Z"]
        else:
            pct = 0
        self._escrever(f"  Diferença para o ótimo: R$ {diferenca:8.2f}   "
                       f"({pct:.1f}% do ótimo)\n\n")

        self._escrever("VEREDITO\n", "titulo")
        if not viavel:
            self._escrever(
                "NÃO COMPENSA - o plano é INVIÁVEL. Ajuste as quantidades para "
                "respeitar o estoque de matéria-prima.\n", "erro")
        elif abs(diferenca) < 0.01:
            self._escrever(
                "EXCELENTE - este plano é exatamente o ÓTIMO neste cenário. "
                "Não há receita maior alcançável com a matéria-prima disponível.\n",
                "ok")
        elif pct >= 95:
            self._escrever(
                f"COMPENSA, mas ainda dá pra melhorar - você está a {pct:.1f}% "
                f"do ótimo. Considere ajustar para {otimo['x1']:.2f} de A e "
                f"{otimo['x2']:.2f} de B para ganhar mais R$ {diferenca:.2f}.\n",
                "aviso")
        else:
            self._escrever(
                f"NÃO COMPENSA - você está deixando R$ {diferenca:.2f} na mesa "
                f"({100-pct:.1f}% abaixo do ótimo). O melhor plano para esses "
                f"preços é produzir {otimo['x1']:.2f} de Liga A e "
                f"{otimo['x2']:.2f} de Liga B (receita R$ {otimo['Z']:.2f}).\n",
                "erro")

    def _carregar_otimo(self):
        try:
            preco_a = self._ler_float(self.var_preco_a.get(), "Preço Liga A")
            preco_b = self._ler_float(self.var_preco_b.get(), "Preço Liga B")
        except ValueError as e:
            messagebox.showerror("Entrada inválida", str(e))
            return
        otimo = resolver_otimo(preco_a, preco_b)
        if otimo is None:
            messagebox.showerror("Erro", "Não foi possível calcular o plano ótimo.")
            return
        self.var_qtd_a.set(str(int(round(otimo["x1"]))))
        self.var_qtd_b.set(str(int(round(otimo["x2"]))))
        self._avaliar()

def main():
    root = tk.Tk()
    PlanejadorLigasApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

