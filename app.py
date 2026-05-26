import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from simplex import resolver


CENARIO_PADRAO = {
    "materiais": ["Cobre", "Zinco", "Chumbo"],
    "limites":   [16, 11, 15],
    "ligas":     ["Liga A", "Liga B"],
    "precos":    [30, 50],
    "composicao": [
        [2, 1],
        [1, 2],
        [1, 3],
    ],
}


def resolver_otimo(limites, precos, composicao):
    saida = resolver("max", precos, composicao, limites, inteiro=True)
    if saida is None:
        return None
    x, z = saida
    return {"x": [int(round(v)) for v in x], "Z": z}


class PlanejadorLigasApp:

    def __init__(self, root):
        self.root = root
        root.title("Planejador de Produção - Fábrica de Ligas Metálicas")
        root.geometry("1100x800")
        root.minsize(950, 700)

        self.var_n_mat = tk.IntVar(value=len(CENARIO_PADRAO["materiais"]))
        self.var_n_lig = tk.IntVar(value=len(CENARIO_PADRAO["ligas"]))

        self.var_materiais = []
        self.var_limites = []
        self.var_ligas = []
        self.var_precos = []
        self.var_composicao = []
        self.var_qtds = []

        self._popular_padrao()

        self._construir_ui()
        self._gerar_tabela()
        self._gerar_plano()

    def _popular_padrao(self):
        self.var_materiais = [tk.StringVar(value=v) for v in CENARIO_PADRAO["materiais"]]
        self.var_limites = [tk.StringVar(value=str(v)) for v in CENARIO_PADRAO["limites"]]
        self.var_ligas = [tk.StringVar(value=v) for v in CENARIO_PADRAO["ligas"]]
        self.var_precos = [tk.StringVar(value=str(v)) for v in CENARIO_PADRAO["precos"]]
        self.var_composicao = [
            [tk.StringVar(value=str(v)) for v in linha]
            for linha in CENARIO_PADRAO["composicao"]
        ]
        self.var_qtds = [tk.StringVar(value="0") for _ in CENARIO_PADRAO["ligas"]]

    def _ajustar_dimensoes(self):
        try:
            n_mat = int(self.var_n_mat.get())
            n_lig = int(self.var_n_lig.get())
        except tk.TclError:
            return
        n_mat = max(1, min(99, n_mat))
        n_lig = max(1, min(26, n_lig))

        while len(self.var_materiais) < n_mat:
            i = len(self.var_materiais) + 1
            self.var_materiais.append(tk.StringVar(value=f"Material {i}"))
            self.var_limites.append(tk.StringVar(value="10"))
            self.var_composicao.append([tk.StringVar(value="0") for _ in range(len(self.var_ligas))])
        while len(self.var_materiais) > n_mat:
            self.var_materiais.pop()
            self.var_limites.pop()
            self.var_composicao.pop()

        while len(self.var_ligas) < n_lig:
            idx = len(self.var_ligas)
            letra = chr(ord("A") + idx) if idx < 26 else str(idx + 1)
            self.var_ligas.append(tk.StringVar(value=f"Liga {letra}"))
            self.var_precos.append(tk.StringVar(value="0"))
            for linha in self.var_composicao:
                linha.append(tk.StringVar(value="0"))
            self.var_qtds.append(tk.StringVar(value="0"))
        while len(self.var_ligas) > n_lig:
            self.var_ligas.pop()
            self.var_precos.pop()
            for linha in self.var_composicao:
                linha.pop()
            self.var_qtds.pop()

        self._gerar_tabela()
        self._gerar_plano()

    def _criar_scroll(self, parent, titulo, max_height=None):
        outer = ttk.LabelFrame(parent, text=titulo, padding=4)
        canvas = tk.Canvas(outer, highlightthickness=0)
        sb_h = ttk.Scrollbar(outer, orient="horizontal", command=canvas.xview)
        canvas.configure(xscrollcommand=sb_h.set)
        sb_v = None
        if max_height is not None:
            sb_v = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=sb_v.set)
        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(_evt=None):
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
                h = bbox[3] - bbox[1]
                if max_height is None:
                    canvas.configure(height=h)
                else:
                    canvas.configure(height=min(h, max_height))
        inner.bind("<Configure>", on_configure)

        canvas.grid(row=0, column=0, sticky="nsew")
        if sb_v is not None:
            sb_v.grid(row=0, column=1, sticky="ns")
        sb_h.grid(row=1, column=0, sticky="ew",
                  columnspan=2 if sb_v is not None else 1)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)
        return outer, inner

    def _construir_ui(self):
        ttk.Label(self.root,
                  text="Planejador de Produção - Fábrica de Ligas Metálicas",
                  font=("TkDefaultFont", 13, "bold")
                  ).pack(pady=(10, 2))
        ttk.Label(self.root,
                  text="Cenário totalmente configurável: nomes, matérias-primas, composições e preços",
                  foreground="gray"
                  ).pack(pady=(0, 8))

        frm_cfg = ttk.LabelFrame(self.root, text="Dimensões do cenário", padding=8)
        frm_cfg.pack(fill="x", padx=10, pady=(0, 6))
        ttk.Label(frm_cfg, text="Nº de matérias-primas:").grid(row=0, column=0, padx=4)
        sp1 = ttk.Spinbox(frm_cfg, from_=1, to=99, width=4,
                          textvariable=self.var_n_mat,
                          command=self._ajustar_dimensoes)
        sp1.grid(row=0, column=1, padx=4)
        ttk.Label(frm_cfg, text="Nº de ligas:").grid(row=0, column=2, padx=(20, 4))
        sp2 = ttk.Spinbox(frm_cfg, from_=1, to=26, width=4,
                          textvariable=self.var_n_lig,
                          command=self._ajustar_dimensoes)
        sp2.grid(row=0, column=3, padx=4)
        ttk.Button(frm_cfg, text="Restaurar exemplo padrão",
                   command=self._restaurar_padrao).grid(row=0, column=4, padx=(20, 4))

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=4)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        col_esq = ttk.Frame(main)
        col_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        col_dir = ttk.Frame(main)
        col_dir.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        outer_tabela, self.frm_tabela = self._criar_scroll(
            col_esq, "Composição, disponibilidade de matéria-prima e preços",
            max_height=300)
        outer_tabela.pack(fill="x", pady=(0, 6))

        outer_plano, self.frm_plano = self._criar_scroll(
            col_esq, "Plano de produção proposto")
        outer_plano.pack(fill="x", pady=6)

        frm_btn = ttk.Frame(col_esq)
        frm_btn.pack(fill="x", pady=(8, 0))
        ttk.Button(frm_btn, text="Avaliar plano",
                   command=self._avaliar).pack(side="left", padx=4)
        ttk.Button(frm_btn, text="Carregar plano ótimo",
                   command=self._carregar_otimo).pack(side="left", padx=4)

        frm_res = ttk.LabelFrame(col_dir, text="Avaliação do plano", padding=8)
        frm_res.pack(fill="both", expand=True)
        self.txt_resultado = scrolledtext.ScrolledText(frm_res, wrap="word",
                                                      font=("Consolas", 10), height=34)
        self.txt_resultado.pack(fill="both", expand=True)
        self.txt_resultado.tag_configure("ok", foreground="#0a7a2e",
                                         font=("TkDefaultFont", 10, "bold"))
        self.txt_resultado.tag_configure("erro", foreground="#b00020",
                                         font=("TkDefaultFont", 10, "bold"))
        self.txt_resultado.tag_configure("aviso", foreground="#b07a00",
                                         font=("TkDefaultFont", 10, "bold"))
        self.txt_resultado.tag_configure("veredito_ok",
                                         foreground="#0a7a2e",
                                         font=("TkDefaultFont", 18, "bold"),
                                         spacing1=8, spacing3=4)
        self.txt_resultado.tag_configure("veredito_aviso",
                                         foreground="#b07a00",
                                         font=("TkDefaultFont", 18, "bold"),
                                         spacing1=8, spacing3=4)
        self.txt_resultado.tag_configure("veredito_erro",
                                         foreground="#b00020",
                                         font=("TkDefaultFont", 18, "bold"),
                                         spacing1=8, spacing3=4)
        self.txt_resultado.tag_configure("subtitulo",
                                         font=("TkDefaultFont", 11, "italic"),
                                         foreground="#444",
                                         spacing3=10)
        self.txt_resultado.configure(state="disabled")

    def _gerar_tabela(self):
        for w in self.frm_tabela.winfo_children():
            w.destroy()

        n_mat = len(self.var_materiais)
        n_lig = len(self.var_ligas)

        ttk.Label(self.frm_tabela, text="Matéria-prima",
                  font=("TkDefaultFont", 10, "bold")
                  ).grid(row=0, column=0, padx=4, pady=4, sticky="w")
        for j in range(n_lig):
            ttk.Entry(self.frm_tabela, textvariable=self.var_ligas[j],
                      width=10, justify="center", font=("TkDefaultFont", 10, "bold")
                      ).grid(row=0, column=1 + j, padx=2, pady=4)
        ttk.Label(self.frm_tabela, text="Disponível",
                  font=("TkDefaultFont", 10, "bold")
                  ).grid(row=0, column=1 + n_lig, padx=(10, 4), pady=4)

        for i in range(n_mat):
            ttk.Entry(self.frm_tabela, textvariable=self.var_materiais[i],
                      width=14, justify="left"
                      ).grid(row=1 + i, column=0, padx=4, pady=2)
            for j in range(n_lig):
                ttk.Entry(self.frm_tabela, textvariable=self.var_composicao[i][j],
                          width=10, justify="center"
                          ).grid(row=1 + i, column=1 + j, padx=2, pady=2)
            ttk.Entry(self.frm_tabela, textvariable=self.var_limites[i],
                      width=10, justify="center"
                      ).grid(row=1 + i, column=1 + n_lig, padx=(10, 4), pady=2)

        linha_preco = 1 + n_mat
        ttk.Label(self.frm_tabela, text="Preço unitário R$",
                  font=("TkDefaultFont", 10, "italic")
                  ).grid(row=linha_preco, column=0, padx=4, pady=(8, 2), sticky="e")
        for j in range(n_lig):
            ttk.Entry(self.frm_tabela, textvariable=self.var_precos[j],
                      width=10, justify="center"
                      ).grid(row=linha_preco, column=1 + j, padx=2, pady=(8, 2))
        ttk.Label(self.frm_tabela, text="—", foreground="gray"
                  ).grid(row=linha_preco, column=1 + n_lig, padx=(10, 4), pady=(8, 2))

    def _gerar_plano(self):
        for w in self.frm_plano.winfo_children():
            w.destroy()

        n_lig = len(self.var_ligas)
        ttk.Label(self.frm_plano,
                  text="Quanto pretende produzir de cada liga?",
                  foreground="gray"
                  ).grid(row=0, column=0, columnspan=2 * n_lig, sticky="w", padx=4, pady=(0, 6))
        for j in range(n_lig):
            ttk.Label(self.frm_plano, textvariable=self.var_ligas[j]
                      ).grid(row=1, column=2 * j, sticky="e", padx=(8, 4), pady=4)
            ttk.Entry(self.frm_plano, textvariable=self.var_qtds[j],
                      width=8, justify="center"
                      ).grid(row=1, column=2 * j + 1, padx=(0, 8), pady=4)

    def _restaurar_padrao(self):
        self.var_n_mat.set(len(CENARIO_PADRAO["materiais"]))
        self.var_n_lig.set(len(CENARIO_PADRAO["ligas"]))
        self._popular_padrao()
        self._gerar_tabela()
        self._gerar_plano()
        self._limpar_resultado()
        self._escrever("Cenário padrão (problema das ligas) restaurado.\n")

    def _escrever(self, texto, tag=""):
        self.txt_resultado.configure(state="normal")
        if tag:
            self.txt_resultado.insert("end", texto, tag)
        else:
            self.txt_resultado.insert("end", texto)
        self.txt_resultado.see("end")
        self.txt_resultado.configure(state="disabled")

    def _limpar_resultado(self):
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        self.txt_resultado.configure(state="disabled")

    def _ler_float(self, valor, nome):
        try:
            return float(str(valor).replace(",", "."))
        except ValueError:
            raise ValueError(f"Valor inválido em '{nome}': '{valor}'.")

    def _coletar_cenario(self):
        n_mat = len(self.var_materiais)
        n_lig = len(self.var_ligas)
        materiais = [v.get().strip() or f"Material {i+1}" for i, v in enumerate(self.var_materiais)]
        ligas = [v.get().strip() or f"Liga {j+1}" for j, v in enumerate(self.var_ligas)]
        limites = [self._ler_float(self.var_limites[i].get(), f"Disponível de {materiais[i]}")
                   for i in range(n_mat)]
        precos = [self._ler_float(self.var_precos[j].get(), f"Preço de {ligas[j]}")
                  for j in range(n_lig)]
        composicao = [[self._ler_float(self.var_composicao[i][j].get(),
                                       f"Composição {materiais[i]}/{ligas[j]}")
                       for j in range(n_lig)]
                      for i in range(n_mat)]
        qtds = [self._ler_float(self.var_qtds[j].get(), f"Quantidade de {ligas[j]}")
                for j in range(n_lig)]
        return materiais, limites, ligas, precos, composicao, qtds

    def _escrever_uso_materiais(self, materiais, consumo, limites):
        self._escrever("\nUso de matéria-prima:\n", "subtitulo")
        for i, nome in enumerate(materiais):
            cons, lim = consumo[i], limites[i]
            sobra = lim - cons
            self._escrever(f"  • {nome}: {cons:g} / {lim:g}   ")
            if sobra > 1e-9:
                self._escrever(f"(sobra {sobra:g})\n", "ok")
            elif sobra < -1e-9:
                self._escrever(f"(falta {-sobra:g})\n", "erro")
            else:
                self._escrever("(totalmente usado)\n", "aviso")

    def _avaliar(self):
        self._limpar_resultado()
        try:
            materiais, limites, ligas, precos, composicao, qtds = self._coletar_cenario()
        except ValueError as e:
            messagebox.showerror("Entrada inválida", str(e))
            return

        if any(q < 0 for q in qtds):
            messagebox.showerror("Entrada inválida", "Quantidades não podem ser negativas.")
            return
        if any(p < 0 for p in precos) or any(l < 0 for l in limites):
            messagebox.showerror("Entrada inválida", "Preços e disponibilidades não podem ser negativos.")
            return

        fracoes = [(ligas[j], qtds[j]) for j in range(len(qtds)) if qtds[j] != int(qtds[j])]
        if fracoes:
            detalhes = ", ".join(f"{n} = {v:g}" for n, v in fracoes)
            messagebox.showerror(
                "Quantidade fracionada não permitida",
                "Uma liga metálica não pode ser produzida em frações.\n"
                f"Corrija para um número inteiro: {detalhes}.")
            return

        n_mat = len(materiais)
        n_lig = len(ligas)
        consumo = [sum(composicao[i][j] * qtds[j] for j in range(n_lig)) for i in range(n_mat)]
        viavel = all(consumo[i] <= limites[i] + 1e-9 for i in range(n_mat))
        receita = sum(precos[j] * qtds[j] for j in range(n_lig))
        otimo = resolver_otimo(limites, precos, composicao)

        partes_seu = " + ".join(f"{int(qtds[j])} {ligas[j]}"
                                for j in range(n_lig) if qtds[j] > 0) or "(nenhuma liga)"

        if not viavel:
            excesso = [(materiais[i], consumo[i], limites[i])
                       for i in range(n_mat) if consumo[i] > limites[i] + 1e-9]
            primeira = excesso[0]
            self._escrever("PLANO INVIÁVEL\n", "veredito_erro")
            self._escrever(
                f"Falta {primeira[1] - primeira[2]:g} unidade(s) de {primeira[0]} "
                f"para esse plano.\n", "subtitulo")
            self._escrever(f"Seu plano:  {partes_seu}\n")
            self._escrever_uso_materiais(materiais, consumo, limites)
            self._escrever("\nReduza a produção para caber no estoque disponível.\n")
            return

        if otimo is None:
            self._escrever("PLANO VIÁVEL\n", "veredito_ok")
            self._escrever(f"Receita: R$ {receita:.2f}\n", "subtitulo")
            self._escrever("(Não foi possível calcular o ótimo para comparação.)\n", "aviso")
            return

        diferenca = otimo["Z"] - receita
        pct = 100 * receita / otimo["Z"] if otimo["Z"] > 1e-9 else 0

        if abs(diferenca) < 0.01:
            self._escrever("CENÁRIO IDEAL\n", "veredito_ok")
            self._escrever("Este é o melhor plano possível com o estoque disponível.\n",
                           "subtitulo")
            self._escrever(f"Produção:  {partes_seu}\n")
            self._escrever(f"Receita:   R$ {receita:.2f}\n")
            return

        partes_otimo = " + ".join(f"{otimo['x'][j]} {ligas[j]}"
                                  for j in range(n_lig) if otimo["x"][j] > 0)

        self._escrever("NÃO É O CENÁRIO IDEAL\n", "veredito_aviso")
        self._escrever(
            f"Você está deixando R$ {diferenca:.2f} na mesa "
            f"({100-pct:.1f}% abaixo do máximo possível).\n",
            "subtitulo")
        self._escrever(f"Seu plano:    {partes_seu}\n")
        self._escrever(f"              R$ {receita:.2f}\n\n")
        self._escrever(f"Plano ideal:  {partes_otimo}\n", "ok")
        self._escrever(f"              R$ {otimo['Z']:.2f}\n", "ok")
        self._escrever_uso_materiais(materiais, consumo, limites)

    def _carregar_otimo(self):
        try:
            _materiais, limites, _ligas, precos, composicao, _qtds = self._coletar_cenario()
        except ValueError as e:
            messagebox.showerror("Entrada inválida", str(e))
            return
        otimo = resolver_otimo(limites, precos, composicao)
        if otimo is None:
            messagebox.showerror("Erro", "Não foi possível calcular o plano ótimo.")
            return
        for j, v in enumerate(otimo["x"]):
            self.var_qtds[j].set(str(v))
        self._avaliar()


def main():
    root = tk.Tk()
    PlanejadorLigasApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
