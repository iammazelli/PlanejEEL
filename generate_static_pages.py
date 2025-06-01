import os, requests, yaml, json
from collections import defaultdict
from flask import Flask, render_template_string

#URLs para dados
URL_YAML = "https://raw.githubusercontent.com/luizeleno/pyjupiter/main/_python/cursos.yml"
BASE_JSON_URL = "https://raw.githubusercontent.com/luizeleno/pyjupiter/main/_python"

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
TEMPLATESPUB_DIR = os.path.join(os.path.dirname(__file__), "templatespub")

app = Flask(__name__, template_folder=TEMPLATES_DIR)
cursos = list()

#função para baixar arquivos
def _baixar(url):
    print(f"[DEBUG]: baixando de {url}\n")
    resp = requests.get(url, timeout = 10)
    resp.raise_for_status()
    return resp.text

#função para pegar a lista de cursos
def get_cursos(url_yaml):
    print("[DEBUG]: coletando e montando lista de cursos\n")
    cursos_yaml = yaml.safe_load(_baixar(url_yaml))
    cursos_nome = list(cursos_yaml) if isinstance(cursos_yaml, dict) else list(cursos_yaml)
    cursos_nome.sort()
    print(f"[DEBUG]: cursos achados: {cursos_nome}\n")
    return cursos_nome

cursos_lista = get_cursos(URL_YAML)

def cursos_json_url(cursos_lista):
    cursos_url_json_lista = list()
    print(f"[DEBUG]: montando a lista dos jsons dos cursos\n")
    for curso in cursos_lista:
        curso_json_url = f"{BASE_JSON_URL}/{curso}.json"
        cursos_url_json_lista.append((curso, curso_json_url))  # Agora é uma tupla
    return cursos_url_json_lista

cursos_url_json_lista = cursos_json_url(cursos_lista)

def get_json_file(curso_json_url):
    print(f"[DEBUG]: baixando arquivos do json de {curso_json_url}\n")
    curso_json = json.loads(_baixar(curso_json_url))
    return curso_json

def make_disciplina_dict(curso_json_file):
    disciplinas = list()
    for item in curso_json_file.items():
        features = item[1] #dicionario
        disciplina = {
            "semestre" : features["semestre"],
            "codigo" : features["sigla"],
            "nome" : features["nomeascii"],
            "docentes" : features["docentes"],
            "requisitos" : features["requisitos"]
        }
        disciplinas.append(disciplina)
    return disciplinas

#print(make_disciplina_dict(get_json_file("https://raw.githubusercontent.com/luizeleno/pyjupiter/main/_python/EA.json")))

def agrupar_por_semestre(disciplinas: list[dict]) -> dict[int, list[dict]]:
    semestres = defaultdict(list)
    for d in disciplinas:
        sem = int(d.get("semestre", 0))
        semestres[sem].append(d)

    for s, lst in sorted(semestres.items()):
        return {s: sorted(lst, key=lambda x: x["codigo"])}

TEMPLATE_STR = """
           {% extends "base.html" %}

{% block title %}Matriz Curricular - {{ curso.nome }}{% endblock %}

{% block content %}
<div class="container-fluid">
    <h1 class="text-center mt-4 mb-5">Grade Curricular - {{ curso.nome }}</h1>

    <div class="alert alert-info text-center" role="alert">
        Selecione as disciplinas nas quais você foi reprovado. Disciplinas travadas serão destacadas em vermelho.
    </div>

    <div class="semestres-container">
        {% for semestre, disciplinas in curso.disciplinas_por_semestre().items() %}
        <div class="card semestre-card m-3 shadow">
            <div class="card-header bg-primary text-white">
                Semestre: {{ semestre }}
            </div>
            <div class="card-body">
                <ul class="list-group">
                    {% for disciplina in disciplinas %}
                    {% set disciplina_id = disciplina.codigo %}
                    <li id="disciplina-{{ disciplina_id }}" class="list-group-item disciplina-item" onclick="toggleSelecao('{{ disciplina_id }}')" onmouseover="mostrarRequisitos('{{ disciplina_id }}')" onmouseout="ocultarRequisitos('{{ disciplina_id }}')">
                        <strong>{{ disciplina.codigo }} - {{ disciplina.nome }}</strong>
                        <div id="requisitos-{{ disciplina_id }}" class="requisitos">
                            <strong>Requisitos:</strong>
                            <ul class="list-group">
                                {% for requisito_codigo in disciplina.requisitos %}
                                {% set requisito = curso.disciplinas[requisito_codigo] %}
                                {% if requisito %}
                                <li id="requisito-{{ requisito.codigo }}" class="list-group-item">{{ requisito.codigo }} - {{ requisito.nome }}</li>
                                {% endif %}
                                {% endfor %}
                            </ul>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<script>
function toggleSelecao(codigoDisciplina) {
    var disciplinaSelecionada = document.getElementById('disciplina-' + codigoDisciplina);
    disciplinaSelecionada.classList.toggle('disciplina-reprovada');
    verificarTravada();
}

function mostrarRequisitos(codigoDisciplina) {
    var requisitosDiv = document.getElementById('requisitos-' + codigoDisciplina);
    if (requisitosDiv) {
        requisitosDiv.style.display = 'block';
    }
}

function ocultarRequisitos(codigoDisciplina) {
    var requisitosDiv = document.getElementById('requisitos-' + codigoDisciplina);
    if (requisitosDiv) {
        requisitosDiv.style.display = 'none';
    }
}

function verificarTravada() {
    var disciplinas = document.querySelectorAll('.disciplina-item');
    var reprovadas = new Set();
    var travadas = new Set();

    disciplinas.forEach(function(disciplina) {
        if (disciplina.classList.contains('disciplina-reprovada')) {
            reprovadas.add(disciplina.id.split('-')[1]);
        }
    });

    function isTravada(codigoDisciplina, visitados = new Set()) {
        if (visitados.has(codigoDisciplina)) {
            return false;  // Evita loops infinitos em caso de dependências circulares
        }
        visitados.add(codigoDisciplina);

        var requisitos = document.querySelectorAll('#requisitos-' + codigoDisciplina + ' li');
        for (var requisito of requisitos) {
            var codigoRequisito = requisito.id.split('-')[1];
            if (reprovadas.has(codigoRequisito) || travadas.has(codigoRequisito) || isTravada(codigoRequisito, visitados)) {
                return true;
            }
        }
        return false;
    }

    disciplinas.forEach(function(disciplina) {
        var codigoDisciplina = disciplina.id.split('-')[1];
        if (isTravada(codigoDisciplina)) {
            disciplina.classList.add('disciplina-travada');
            travadas.add(codigoDisciplina);
        } else {
            disciplina.classList.remove('disciplina-travada');
            travadas.delete(codigoDisciplina);
        }
    });
}

// Adiciona classe ao body baseado na largura da viewport
function ajustarLayout() {
    var viewportWidth = window.innerWidth;
    var semestreContainer = document.querySelector('.semestres-container');
    
    if (viewportWidth >= 1200) {
        semestreContainer.classList.add('colunas-full');
    } else {
        semestreContainer.classList.remove('colunas-full');
    }
}

window.addEventListener('load', ajustarLayout);
window.addEventListener('resize', ajustarLayout);

</script>

<style>
/* Estilos para o container principal dos semestres */
.semestres-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    width: flex;
    max-width: 100vw; /* Largura máxima do container igual à largura da viewport */
    margin: 0 auto; /* Centraliza o container na página */
}

/* Estilos para cada cartão de semestre */
.semestre-card {
    flex: 2 1 calc(17.5% - 20px); /* Cada card ocupa metade da largura disponível menos o espaço entre as colunas */
    width: 200px;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease-in-out;
    background-color: #fff;
}

.semestre-card:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.card-header {
    padding: 10px 15px;
    background-color: #007bff;
    color: #fff;
    border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.card-body {
    padding: 15px;
}

.list-group-item {
    cursor: pointer;
}

.requisitos {
    margin-top: 10px;
    display: none;
}

.disciplina-reprovada {
    background-color: #ffd700;
}

.disciplina-travada {
    background-color: #ffcccc;
}

.text-center {
    text-align: center;
}

footer {
    margin-top: 20px;
}

/* Layout responsivo baseado na largura da viewport */
.colunas-quatro {
    justify-content: space-between;
}

.colunas-dois {
    justify-content: space-between;
}

.colunas-um {
    justify-content: center;
}

@media (min-width: 1200px) {
    .colunas-full {
        justify-content: space-around;
    }
}

@media (min-width: 992px) and (max-width: 1199px) {
    .semestre-card {
        flex: 1 1 calc(50% - 20px);
    }
}

@media (max-width: 991px) {
    .semestre-card {
        flex: 1 1 100%;
    }
}
</style>

{% endblock %}

            """

def gerar_paginas(cursos_url_json_lista):
    os.makedirs(TEMPLATESPUB_DIR, exist_ok=True)

    for sigla, url in cursos_url_json_lista:
        dados_json = get_json_file(url)
        disciplinas = make_disciplina_dict(dados_json)
        por_semestre = agrupar_por_semestre(disciplinas)

        # Criar um objeto curso simulado com os dados necessários
        curso = {
            'nome': sigla,  # Ou outro nome mais descritivo se disponível
            'disciplinas_por_semestre': lambda: por_semestre,
            'disciplinas': {d['codigo']: d for d in disciplinas}
        }

        with app.app_context():
            html = render_template_string(
                TEMPLATE_STR,
                curso=curso,  # Agora passando o objeto curso
                sigla=sigla,
                por_semestre=por_semestre
            )

        arquivo = os.path.join(TEMPLATESPUB_DIR, f"{sigla}.html")
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"[INFO] Página gerada: {arquivo}")

if __name__ == "__main__":
    cursos_lista = get_cursos(URL_YAML)
    cursos_url_json_lst = cursos_json_url(cursos_lista)
    gerar_paginas(cursos_url_json_lst)
    print("[INFO] Geração concluída!")
