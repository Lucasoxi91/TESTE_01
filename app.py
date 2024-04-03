from flask import Flask, render_template, request
import os
import importlib.util
import random

app = Flask(__name__)
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')

COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

def list_scripts():
    """Lista os scripts Python disponíveis na pasta 'scripts'."""
    return [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]

def execute_script(script_name):
    """Executa a função 'execute_query' do script selecionado e retorna seus resultados."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    spec = importlib.util.spec_from_file_location("module.name", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.execute_query()

@app.route('/')
def index():
    scripts = list_scripts()
    return render_template('index.html', scripts=scripts)
@app.route('/some_route')
def some_route():
    result_data = some_function()  # Chama a função e armazena o resultado.
    data = {
        'result': result_data,  # Passa os resultados, não a função.
    }
    return render_template('template.html', data=data)

@app.route('/execute', methods=['GET'])
def execute():
    script_name = request.args.get('script')
    display_mode = request.args.get('display', 'tabela')  # Assume 'tabela' como padrão

    if script_name in list_scripts():
        column_names, query_results = execute_script(script_name)

        # Inicializa 'data' para evitar NameError
        data = {'labels': [], 'values': [], 'backgroundColor': [], 'borderColor': []}

        if display_mode == 'barras' or display_mode == 'pizza':
            categories = [row[0] for row in query_results]  # Assume que a 1ª coluna é a categoria
            values = [row[1] for row in query_results]  # Assume que a 2ª coluna é o valor numérico
            # Supõe-se aqui que a lógica para definir 'colors' já foi feita
            colors = ['#1f77b4', '#ff7f0e', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

            # Prepara 'data' com os valores necessários
            categories = ['Categoria 1', 'Categoria 2', 'Categoria 3']  # Exemplo
            values = [100, 200, 300]  # Exemplo
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Exemplo

            data = {             
                'labels': categories,
                'values': values,
                'backgroundColor': colors,
                'borderColor': colors,
            }

        if display_mode in ['barras', 'pizza']:
            return render_template('grafico.html', script_name=script_name, data=data, display_mode=display_mode, column_names=column_names)
        else:
            # Caso 'display_mode' seja 'tabela' ou qualquer outro valor não reconhecido
            # Não precisa passar 'data' para a visualização em tabela
            return render_template('tabela.html', script_name=script_name, column_names=column_names, query_results=query_results)
    else:
        return "Script not found", 404

    
if __name__ == '_main_':
    app.run(debug=True)