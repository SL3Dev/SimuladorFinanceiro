import tkinter as tk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import pandas as pd


def calcular_investimento(preco_produto, meses, aporte_mensal, num_parcelas, cdi_anual, bancos):
    resultados = []
    total_parcelado = preco_produto if num_parcelas == 0 else (preco_produto / num_parcelas) * num_parcelas

    for banco, percentual_cdi in bancos.items():
        rentabilidade_anual = (percentual_cdi / 100) * cdi_anual
        rentabilidade_mensal = (1 + rentabilidade_anual / 100) ** (1/12) - 1

        saldo = preco_produto
        historico = []
        for mes in range(1, meses + 1):
            saldo = saldo * (1 + rentabilidade_mensal) + aporte_mensal
            historico.append((mes, saldo))

        ganho = saldo - preco_produto - aporte_mensal * meses
        compensa = saldo > total_parcelado

        resultados.append({
            "banco": banco,
            "cdi_percentual": percentual_cdi,
            "rent_anual": rentabilidade_anual,
            "saldo_final": saldo,
            "ganho": ganho,
            "compensa": compensa,
            "historico": historico
        })

    return resultados, total_parcelado


def gerar_pdf(resultados, total_parcelado, filepath):
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Relatório de Simulação de Investimento com CDI")
    y -= 30

    c.setFont("Helvetica", 10)
    for r in resultados:
        c.drawString(50, y, f"Banco: {r['banco']}")
        y -= 15
        c.drawString(70, y, f"CDI: {r['cdi_percentual']}% | Rent. Anual: {r['rent_anual']:.2f}%")
        y -= 15
        c.drawString(70, y, f"Saldo Final: R$ {r['saldo_final']:.2f} | Ganho: R$ {r['ganho']:.2f}")
        y -= 15
        situacao = "Compensa investir e parcelar" if r['compensa'] else "Não compensa investir e parcelar"
        c.drawString(70, y, situacao)
        y -= 30

        if y < 100:
            c.showPage()
            y = height - 50

    c.drawString(50, y, f"Total parcelado (sem juros): R$ {total_parcelado:.2f}")
    c.save()


def gerar_grafico(resultados):
    bancos = [r['banco'] for r in resultados]
    saldos = [r['saldo_final'] for r in resultados]

    plt.figure(figsize=(8, 5))
    plt.bar(bancos, saldos, color='#4caf50')
    plt.title("Saldo Final por Banco")
    plt.ylabel("Saldo Final (R$)")
    plt.xlabel("Banco")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def exportar_excel(resultados, filepath):
    df = pd.DataFrame([{ 
        'Banco': r['banco'],
        'CDI %': r['cdi_percentual'],
        'Rent. Anual %': r['rent_anual'],
        'Saldo Final': r['saldo_final'],
        'Ganho': r['ganho'],
        'Compensa': r['compensa']
    } for r in resultados])

    df.to_excel(filepath, index=False)


def executar_simulacao():
    try:
        preco_produto = float(entry_preco.get())
        meses = int(entry_meses.get())
        aporte_mensal = float(entry_aporte.get())
        num_parcelas = int(entry_parcelas.get())
        cdi_anual = float(entry_cdi_anual.get())

        bancos = {}
        linhas = text_bancos.get("1.0", tk.END).strip().splitlines()
        for linha in linhas:
            nome, cdi = linha.split(";")
            bancos[nome.strip()] = float(cdi.strip())

        resultados, total_parcelado = calcular_investimento(
            preco_produto, meses, aporte_mensal, num_parcelas, cdi_anual, bancos)

        output.delete("1.0", tk.END)
        for r in resultados:
            output.insert(tk.END, f"Banco: {r['banco']}\n")
            output.insert(tk.END, f"Saldo Final: R$ {r['saldo_final']:.2f} | Ganho: R$ {r['ganho']:.2f}\n")
            situacao = "✅ Compensa investir e parcelar" if r['compensa'] else "⚠️ Não compensa investir e parcelar"
            output.insert(tk.END, situacao + "\n\n")

        def salvar_pdf():
            filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if filepath:
                gerar_pdf(resultados, total_parcelado, filepath)
                messagebox.showinfo("Sucesso", "Relatório PDF salvo com sucesso!")

        def salvar_excel():
            filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if filepath:
                exportar_excel(resultados, filepath)
                messagebox.showinfo("Sucesso", "Relatório Excel salvo com sucesso!")

        btn_pdf.config(command=salvar_pdf)
        btn_excel.config(command=salvar_excel)
        gerar_grafico(resultados)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro na simulação: {e}")


janela = tk.Tk()
janela.title("Simulador CDI - Comparativo de Compra")
janela.configure(bg="#f0f4f7")

frame = tk.Frame(janela, bg="#f0f4f7")
frame.pack(padx=10, pady=10)

campos = [
    ("Preço do Produto (R$)", "preco"),
    ("Meses para render", "meses"),
    ("Aporte mensal adicional (R$)", "aporte"),
    ("Número de parcelas (0 se não parcelado)", "parcelas"),
    ("CDI anual base atual (%)", "cdi_anual")
]

for texto, var in campos:
    tk.Label(frame, text=texto, bg="#f0f4f7").pack(anchor="w")
    globals()[f"entry_{var}"] = tk.Entry(frame)
    globals()[f"entry_{var}"].pack(fill="x", pady=2)

tk.Label(frame, text="Bancos e Percentual CDI (nome; percentual)", bg="#f0f4f7").pack(anchor="w", pady=5)
text_bancos = tk.Text(frame, height=4)
text_bancos.pack(fill="x")

tk.Button(frame, text="💡 Simular", bg="#4caf50", fg="white", command=executar_simulacao).pack(fill="x", pady=5)
btn_pdf = tk.Button(frame, text="📄 Exportar PDF", bg="#2196f3", fg="white")
btn_pdf.pack(fill="x", pady=5)
btn_excel = tk.Button(frame, text="📊 Exportar Excel", bg="#ff9800", fg="white")
btn_excel.pack(fill="x", pady=5)

output = tk.Text(janela, height=12, bg="white")
output.pack(fill="both", expand=True, padx=10, pady=10)

janela.mainloop()
