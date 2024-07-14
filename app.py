from flask import Flask, render_template, request
import requests
import yaml

app = Flask(__name__)

class Disciplina:
    def __init__(self, codigo, nome, semestre, tipo, requisitos):
        self.codigo = codigo
        self.nome = nome
        self.semestre = semestre
        self.tipo = tipo
        self.requisitos = requisitos

class Curso:
    def __init__(self, nome):
        self.nome = nome
        self.disciplinas = []

    def disciplinas_por_semestre(self):
        semestres = {}
        for disciplina in self.disciplinas:
            if disciplina.semestre not in semestres:
                semestres[disciplina.semestre] = []
            semestres[disciplina.semestre].append(disciplina)
        return semestres

def carregar_cursos_do_yaml(url_yaml):
    cursos = []
    try:
        response = requests.get(url_yaml)
        if response.status_code == 200:
            dados_yaml = yaml.safe_load(response.text)
            for curso_nome in dados_yaml.keys():
                curso = Curso(curso_nome)
                disciplinas = carregar_disciplinas_do_json(curso_nome)
                if disciplinas:
                    curso.disciplinas.extend(disciplinas)
                cursos.append(curso)
            return cursos
        else:
            print(f"Erro ao acessar o arquivo YAML: {response.status_code} {response.reason}")
            return None
    except Exception as e:
        print(f"Erro ao carregar dados do YAML: {e}")
        return None

def carregar_disciplinas_do_json(curso_nome):
    try:
        url_json = f"https://raw.githubusercontent.com/luizeleno/pyjupiter/main/_python/{curso_nome}.json"
        response = requests.get(url_json)
        if response.status_code == 200:
            dados_json = response.json()
            disciplinas = []
            for disciplina_codigo, disciplina_dados in dados_json.items():
                if disciplina_dados.get("tipo") == "Obrigatórias":
                    nome_disciplina = disciplina_dados.get("nomeascii", "Nome da Disciplina Desconhecido")
                    semestre_disciplina = disciplina_dados.get("semestre", "Semestre Desconhecido")
                    tipo_disciplina = disciplina_dados.get("tipo", "Tipo Desconhecido")
                    requisitos_disciplina = disciplina_dados.get("requisitos", [])
                    disciplina = Disciplina(disciplina_codigo, nome_disciplina, semestre_disciplina, tipo_disciplina, requisitos_disciplina)
                    disciplinas.append(disciplina)
            return disciplinas
        else:
            print(f"Erro ao acessar o arquivo JSON para o curso {curso_nome}: {response.status_code} {response.reason}")
            return None
    except Exception as e:
        print(f"Erro ao carregar disciplinas do JSON para o curso {curso_nome}: {e}")
        return None

url_yaml = "https://raw.githubusercontent.com/luizeleno/pyjupiter/main/_python/cursos.yml"

@app.route('/')
def index():
    cursos = carregar_cursos_do_yaml(url_yaml)
    return render_template('index.html', cursos=cursos)

@app.route('/curso')
def curso():
    curso_nome = request.args.get('curso_nome')
    cursos = carregar_cursos_do_yaml(url_yaml)
    curso_encontrado = next((curso for curso in cursos if curso.nome == curso_nome), None)
    if curso_encontrado:
        return render_template('curso.html', curso=curso_encontrado)
    else:
        return "Curso não encontrado", 404

if __name__ == '__main__':
    app.run(debug=True)
