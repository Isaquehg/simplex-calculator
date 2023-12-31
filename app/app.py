from flask import Flask, render_template, request, redirect, url_for
from utils.simplex import Simplex

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/ppl/setup', methods=['GET', 'POST'])
def ppl_setup():
    # Ao clicar em continuar, depois da config. inicial do PPL
    if request.method == 'POST':
        #print(request.form)
        #ImmutableMultiDict([('num_variaveis', '2'), ('tipo_problema', 'max'), ('num_restricoes', '5')])

        global num_variaveis
        global num_restricoes
        num_variaveis = int(request.form['num_variaveis'])
        num_restricoes = int(request.form['num_restricoes'])

        # Redireciona para outra rota
        return render_template('modelo-ppl.html', num_variaveis=num_variaveis, num_restricoes=num_restricoes)

    return render_template('index.html')

# Ao clicar para obter o resultado final do PPL
@app.route('/ppl/evaluate', methods=['POST'])
def evaluate():
    # Realizar operações necessárias com os coeficientes recebidos do usuário
    # Então retornar o template de resultado final do PPL, com ponto ótimo, lucro ótimo e o preço-sombra de cada restrição

    #print(f'keys: {len(request.form.keys())}')
    #print(f'form: {request.form}')
    '''
    {'coef_objetivo0': '5', 'coef_objetivo1': '9', 'coef_restricao00': '3', 'coef_restricao01': '0', 'lado_direito_0': '20', 'sinal_inequacao_0': 'less', 'coef_restricao10': '0', 'coef_restricao11': '1', 'lado_direito_1': '45', 'sinal_inequacao_1': 'less', 'coef_restricao20': '2', 'coef_restricao21': '5', 'lado_direito_2': '100', 'sinal_inequacao_2': 'greater', 'coef_restricao30': '4', 'coef_restricao31': '1', 'lado_direito_3': '45', 'sinal_inequacao_3': 'greater', 'coef_restricao40': '1', 'coef_restricao41': '1', 'lado_direito_4': '2', 'sinal_inequacao_4': 'less', 'coef_restricao50': '1', 'coef_restricao51': '1', 'lado_direito_5': '0', 'sinal_inequacao_5': 'greater', 'tipo_problema': 'max'}
    Tipo Problema: max
    Num. Variáveis: 2
    Num. Restrições: 3
    Coefs Objetivo: [200.0, 300.0]
    Coefs Restrições: [50.0, 60.0, 80.0, 90.0, 110.0, 120.0]
    Lados Direitos: [400.0, 70.0, 100.0, 130.0, 500.0, 350.0]
    '''

    data = dict(request.form)
    print(data)

    # Initialize lists to store coefficients
    coefs_func_objetivo = []
    coefs_restricao = []
    lados_direitos = []
    sinais = []

    # Extrair componentes do request
    for key, value in data.items():
        if key.startswith('coef_objetivo'):
            coefs_func_objetivo.append(float(value))
        elif key.startswith('coef_restricao'):
            coefs_restricao.append(float(value))
        elif key.startswith('lado_direito'):
            lados_direitos.append(float(value))
        elif key.startswith('sinal_inequacao'):
            sinais.append(value)

    # Transformando os coeficientes em negativo
    coefs_func_objetivo = [-coef for coef in coefs_func_objetivo]

    # Convertendo lista de restrições para Array de restrições
    restricoes_array = []  # Initialize as an empty list
    for i in range(num_restricoes):
        # Initialize the sublist for each row
        row_list = []
        for j in range(num_variaveis):
            row_list.append(coefs_restricao[j + i * num_variaveis])  # Adjust the index to get the correct coefficient
        restricoes_array.append(row_list)

    coefs_restricao = restricoes_array

    print(f'Num. Variáveis: {num_variaveis}')
    print(f'Num. Restrições: {num_restricoes}')
    print(f'Coefs Objetivo: {coefs_func_objetivo}')
    print(f'Coefs Restrições: {coefs_restricao}')
    print(f'Lados Direitos: {lados_direitos}')
    print(f'Sinais das restricoes: {sinais}')

    # Instanciar calculadora Simplex
    simplex_calculator = Simplex(coefs_func_objetivo, coefs_restricao, lados_direitos, sinais)

    # Resultados
    optimal_solution, optimal_values, shadow_prices, tableau = simplex_calculator.get_results()

    # Formatação da saída do tableau (Converter tudo para string)
    tableau[0][0] = "LD"
    for index_row, row in enumerate(tableau):
        for index_col, value in enumerate(row):
            if (type(value) is not str):
                tableau[index_row, index_col] = str(value)

    print(f'\n\noptimal_solution: {optimal_solution}\n')

    print(f'optimal_value: {optimal_values}\n')

    print(f'shadow_prices: {shadow_prices}\n')

    print(f'tableau: {tableau}')
    print(type(tableau[2,3]))

    results = {
        "profit": optimal_solution,
        "optimal_values": optimal_values,
        "shadow_prices": shadow_prices,
        "tableau": tableau
    }

    return render_template('success.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
