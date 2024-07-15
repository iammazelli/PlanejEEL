from flask import Flask, render_template, request
import requests
import yaml
import os
import re
from unicodedata import normalize

app = Flask(__name__)

class Disciplina:
    def __init__(self, codigo, nome, semestre, tipo, requisitos):
        self.codigo = codigo
        self.nome = nome
        self.semestre = semestre
        self.tipo = tipo
        self.requisitos = requisitos  # Lista de códigos de requisitos

class Curso:
    def __init__(self, nome):
        self.nome = nome
        self.disciplinas = {}

    def disciplinas_por_semestre(self):
        semestres = {}
        for codigo, disciplina in self.disciplinas.items():
            semestre = disciplina.semestre
            if semestre not in semestres:
                semestres[semestre] = []
            semestres[semestre].append(disciplina)
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
                    for codigo, disciplina in disciplinas.items():
                        curso.disciplinas[codigo] = disciplina
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
            disciplinas = {}
            for disciplina_codigo, disciplina_dados in dados_json.items():
                if disciplina_dados.get("tipo") == "Obrigatórias":
                    nome_disciplina = disciplina_dados.get("nomeascii", "Nome da Disciplina Desconhecido")
                    semestre_disciplina = disciplina_dados.get("semestre", "Semestre Desconhecido")
                    tipo_disciplina = disciplina_dados.get("tipo", "Tipo Desconhecido")
                    requisitos_disciplina = disciplina_dados.get("requisitos", [])
                    
                    # Limpar caracteres especiais dos códigos de disciplina e requisitos
                    disciplina_codigo_limpo = limpar_codigo(disciplina_codigo)
                    nome_disciplina_limpo = limpar_nome(nome_disciplina)
                    
                    disciplina = Disciplina(disciplina_codigo_limpo, nome_disciplina_limpo, semestre_disciplina, tipo_disciplina, requisitos_disciplina)
                    disciplinas[disciplina_codigo_limpo] = disciplina
            return disciplinas
        else:
            print(f"Erro ao acessar o arquivo JSON para o curso {curso_nome}: {response.status_code} {response.reason}")
            return None
    except Exception as e:
        print(f"Erro ao carregar disciplinas do JSON para o curso {curso_nome}: {e}")
        return None


def limpar_codigo(codigo):
    return re.sub(r'\W+', '', codigo)

def limpar_nome(nome):
    return normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')

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
