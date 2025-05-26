import time, plotly
from shiny import App, reactive, render, ui

# CSS
custom_css = ui.tags.style("""
    body {
        background-color: #f7f9fc;

    }
    h2 {
        color: #2F4F4F;
        margin-top: 20px;
        font-family: "Trebuchet MS", Tahoma, sans-serif;
    }
    h3 {
        color: #2F4F4F;
        font-family: 'Segoe UI', sans-serif;
        font-size: 18px;

    }
    .shiny-input-container {
        margin-bottom: 20px;
    }
    .btn-primary {
        background-color: #4CAF50;
        border: none;
    }
""")

# interface do usuário
app_ui = ui.page_fluid(
    custom_css,  # aplica o estilo
    ui.h2("Calculadora de IMC (Índice de massa corporal)"),
    ui.hr(),

    ui.h3("O Índice de Massa Corporal (IMC) é uma medida utilizada para avaliar se uma pessoa " \
    "está dentro de um peso saudável. Ele é calculado dividindo o peso (KG) pela altura ao quadrado (m²)." \
    " Manter um IMC adequado contribui para uma melhor saúde cardiovascular, reduzir riscos de diabetes e melhorar a qualidade de vida."),
    ui.h3("Exemplo: Se uma pessoa pesa 70 kg e tem 1,70 m de altura, o cálculo seria: IMC = 70 kg / (1,70 m)², IMC = 70 kg / 2,89 m², IMC = 24,22."),
    ui.br(),


    ui.row(
        ui.column(6,
            ui.input_text("nome", "Nome", placeholder="Digite seu nome"),
            ui.input_select("genero", "Gênero", {"Feminino": "Feminino", "Masculino": "Masculino", "Prefiro não dizer":"Prefiro não dizer"})
        ),
        ui.column(6,
            ui.input_numeric("altura", "Altura (cm)", value=0.00, min=0.0, max=300.00),
            ui.input_numeric("peso", "Peso (KG)", value=0.00, min=1.00, max=350.00),
        )
    ),

    ui.hr(),
    ui.input_action_button("calcular", "Calcular IMC", class_="btn-primary"),
    ui.br(),
    ui.output_ui("progresso"),
    ui.br(),
    ui.output_ui("resultado"),
    ui.br(),
    ui.output_plot("grafico_imc") 

)

# lógica 
def server(input, output, session):
    @output
    @render.ui
    @reactive.event(input.calcular)
    def progresso():
        nome = input.nome().strip()
        with ui.Progress(min=1, max=5) as p:# cria a barra de progresso, sendo de 1 a 5
            p.set(message="Calculando seu IMC...", detail="Isso pode levar alguns segundos...")
            for i in range(1, 6):# Loop que simula etapas do carregamento
                p.set(i, detail=f"Etapa {i}/5")
                time.sleep(0.2) # tempo definido para demorar em cada etapa 
        return ui.br(),ui.h3(f"Se tiver pendência, por favor, insira o campo solicitado. Caso não, segue o resultado {nome}:")

    @output
    @render.ui
    @reactive.event(input.calcular) # executa após clicar no botão calcular
    def resultado():
        nome = input.nome().strip() # chama a variável e permite que retire os espaços caso tenha um nome composto, por exemplo
        genero = input.genero()
        peso = input.peso()
        altura_cm = input.altura()

        if not nome:
            return ui.h3("Por favor, digite seu nome.")
        if altura_cm == 0:
            return ui.h3("Por favor, insira sua altura (cm).")
        elif peso == 0:
            return ui.h3("Por favor, insira seu peso (kg).")

        altura_m = altura_cm / 100
        imc = peso / (altura_m ** 2)

        classificacao = (
            "abaixo do peso" if imc < 18.5 else
            "com peso normal" if imc < 25 else
            "com sobrepeso" if imc < 30 else
            "com obesidade grau I" if imc < 35 else
            "com obesidade grau II" if imc < 40 else
            "com obesidade grau III"
        )
        return ui.h3(f"Seu IMC é {imc:.2f}, o que indica que você está {classificacao}.")
    
    @output
    @render.plot
    @reactive.event(input.calcular) # executa após clicar no botão calcular
    def grafico_imc():
        import matplotlib.pyplot as plt
        nome = input.nome().strip()
        peso = input.peso()
        altura_cm = input.altura()

        # caso algum campo não seja preenchido, o gráfico não é gerado
        if not nome or altura_cm == 0 or peso == 0:
            return None
        
        altura_m = altura_cm / 100
        imc = peso / (altura_m ** 2)
        imc_ideal = 24.9
        # dados do gráfico
        categorias = ["IMC ideal", "Seu IMC"]
        valores = [imc_ideal, imc]
        cores = ["#378C3A", "#803131"]

        fig, ax = plt.subplots(figsize=(5, 4)) # cria o gráfico e ajusta o tamanho do mesmo
        bars = ax.bar(categorias, valores, color=cores, width=0.4) # cria as barras

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2, # encontra o meio da barra, para colocar o texto bem centralizado
                height, # coloca o texto na altura da barra (topo)
                f'{height:.1f}', # para mostrar uma casa decimal (24.9)
                ha='center',
                va='bottom', # faz o texto ficar acima da barra
                fontsize=12
            )

        ax.set_title("Comparação: IMC do peso ideal e seu IMC") # título
        ax.set_ylabel("Valor do IMC") # nome do Y
        ax.set_ylim(0, max(40, imc + 10)) # coloca o valor máximo do x, enquanto for menor que 40. Caso o valor ser superior, soma o valor do IMC + 10 para aparecer na lateral Y
        ax.set_xlim(-0.5, 1.5)  # Aproxima as barras lateralmente


# Executa o app
app = App(app_ui, server)
