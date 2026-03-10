# Radar Cidadão 🕵️ <a id="topo"></a>

<p align="center">
      <img src="https://via.placeholder.com/200" alt="Logo do Grupo Lumina" width="200">
      <h2 align="center"> Grupo Lumina </h2>
</p>

<p align="center">
  <a href="#desafio">Desafio</a> | 
  <a href="#backlog">Backlog</a> | 
  <a href="#dor">DoR</a> | 
  <a href="#dod">DoD</a> | 
  <a href="#sprint">Cronograma</a> | 
  <a href="#tecnologias">Tecnologias</a> | 
  <a href="#execucao">Como Executar</a> | 
  <a href="#equipe">Equipe</a> | 
  <a href="#professores">Professores</a>
</p>

> **Status do Projeto:** Planejamento (Sprint 1) 🛠️
>
> **Repositório da Organização:** [Link para o Repo]

---

## 🏅 Desafio <a id="desafio"></a>

O projeto **Radar Cidadão** surge da necessidade de tornar a democracia mais acessível através da transparência de dados. O foco central é a análise de desempenho dos Deputados Federais que buscam a reeleição, utilizando como fonte a API pública da Câmara dos Deputados.

### 1. Contexto
Em outubro de 2026, ocorrerão as eleições para Deputado Federal. Embora os dados sobre presença, gastos e atividades parlamentares sejam públicos, eles se apresentam de forma técnica, dispersa e de difícil interpretação para a maioria da população. Nosso objetivo é transformar essa complexidade em informação clara e útil.

---

### 2. Dores do Parceiro
Para garantir que a solução seja funcional, focamos em três perfis de usuários (Personas) identificados pelo parceiro:

<details open><summary><b>Educação (Profª Ana Lúcia):</b></summary> Necessidade de ensinar cidadania baseada em fatos e dados neutros, mas falta de ferramentas que organizem o desempenho dos candidatos de forma estruturada.</details>
<br>
<details open><summary><b>Jornalismo (Carlos Menezes)::</b></summary> Necessidade de avaliar rapidamente o desempenho de deputados estaduais em busca de reeleição, enfrentando o desafio de dados complexos e espalhados.</details>
<br>
<details open><summary><b>Cidadania (Dona Maria):</b></summary> Desejo de votar com consciência, mas sente falta de uma síntese simples e objetiva para decidir se deve ou não reconduzir seu representante.</details>

---

### 3. Problema Central
Atualmente, eleitores e educadores não possuem ferramentas simples e neutras para avaliar o desempenho de deputados federais candidatos à reeleição.
> **Pergunta Investigativa:** [Título Provisório: Como transformar dados públicos complexos em informação compreensível?] 

<br>
<p align="right"><a href="#topo">↑ Voltar ao topo</a></p>

## 📋 Backlog do Produto <a id="backlog"></a>

O Backlog do Produto representa a lista de todas as funcionalidades e entregas planejadas para o projeto **Radar Cidadão**, priorizadas de acordo com o valor entregue ao cidadão.

| Rank | Prioridade | User Story | Estimativa | Sprint | Critério de Aceitação |
| :--: | :----: | :--------- | :----: | :----: | :-------------------- |
| 1 | ⬛ | Como desenvolvedor, quero configurar o ambiente e acessar a API da Câmara para coletar dados dos deputados. | ⚫ | 1 | Conexão com API estabelecida e dados brutos (JSON) salvos no Google Colab.  |
| 2 | ⬛ | Como desenvolvedor, quero criar um script de limpeza para remover registos duplicados ou nulos da API. | ⚫ | 1 | Dados no Colab sem inconsistências (ex.: deputados sem nome).  |
| 3 | ⬛ | Como eleitor, quero ver um gráfico simples da presença do meu deputado para decidir meu voto. | ⚫ | 1 | Gráfico de presença gerado no Colab com tratamento inicial de dados.  |
| 4 | ⬛ | Como usuário, quero acessar a página inicial do site para entender o propósito do projeto. | ⚫ | 1 | Esboço do site em Flask funcional (mesmo sem dados reais).  |
| 5 | ⬛ | Como desenvolvedor, quero persistir os dados tratados no banco de dados para o site. | ⚫ | 2 | Banco MariaDB/MySQL populado sem uso de ORM.  |
| 6 | ⬛ | Como professor, quero comparar gastos de deputados por partido para ensinar cidadania. | ⚫ | 2 | Página de consulta por partido que exiba indicadores de despesas médias.  |
| 7 | ⬛ | Como jornalista, quero filtrar deputados por estado para avaliar o desempenho local rapidamente. | ⚫ | 2 | Sistema de busca/filtro por estado funcionando com navegação intuitiva.  |
| 8 | ⬛ | Como eleitor, quero ver fotos dos deputados no site para os identificar mais facilmente. | ⚫ | 2 | O site deve renderizar a URL da imagem fornecida pela API da Câmara.  |
| 9 | ⬛ | Como desenvolvedor, quero um script SQL de criação de tabelas (Schema) que respeite as chaves primárias e estrangeiras. | ⚫ | 2 | Script.sql funcional que cria a estrutura no banco sem erros de integridade.  |
| 10 | ⬛ | Como usuário, quero uma barra de pesquisa por nome para encontrar um deputado específico rapidamente. | ⚫ | 2 | Campo de input que filtra a lista de deputados em tempo real ou via submissão de formulário.  |
| 11 | ⬛ | Como equipe, queremos realizar testes de navegação para garantir que o utilizador chegue à informação com poucos cliques. | ⚫ | 3 | Relatório simples de teste de usabilidade para validar a navegação.  |
| 12 | ⬛ | Como usuário, quero uma página de erro caso procure por um deputado inexistente. | ⚫ | 3 | Template Flask customizado para erros de rota ou dados não encontrados.  |
| 13 | ⬛ | Como professor, quero ver legendas explicativas nos gráficos (ex.: o que é "cota parlamentar" etc). | ⚫ | 3 | Glossário que explique termos técnicos legislativos de forma simples.  |
| 14 | ⬛ | Como desenvolvedor, quero documentar o README do GitHub com instruções de instalação e execução do projeto. | ⚫ | 3 | Ficheiro README.md contendo requisitos, o backlog, como configurar o BD e como rodar o sistema.  |

---

<br>
<p align="right"><a href="#topo">↑ Voltar ao topo</a></p>

## 🏃‍ DoR - Definition of Ready <a id="dor"></a>
Para que uma tarefa seja considerada pronta para iniciar (Ready), ela deve possuir:
* Descrição clara da funcionalidade.
* Critérios de aceitação definidos.
* Dados necessários da API identificados.

## 🏆 DoD - Definition of Done <a id="dod"></a>
Uma tarefa é considerada concluída (Done) quando:
* O código segue os padrões de commit da Fatec.
* A funcionalidade foi testada e está estável na branch `main`.
* A documentação técnica foi atualizada no repositório.

<br>
<p align="right"><a href="#topo">↑ Voltar ao topo</a></p>

## 📅 Cronograma de Evolução do Projeto <a id="sprint"></a>

O projeto está dividido em três Sprints, seguindo a metodologia ágil Scrum. O progresso atual é atualizado ao final de cada ciclo.

---

### 📑 Tabela Descritiva das Sprints

| Sprint | Período | Conteúdo (Foco) | Documentação | Vídeo de Entrega | Status |
| :---: | :---: | :--- | :---: | :---: | :---: |
| **01** | 00/00 a 00/00 | Análise de dados no Colab e Estrutura Inicial Flask | [Acessar](./docs/sprint1) | [Assistir](#) | 🏗️ Em curso |
| **02** | 00/00 a 00/00 | Banco de Dados MariaDB e Filtros de Pesquisa | [Acessar](./docs/sprint2) | [Assistir](#) | 📅 Planejado |
| **03** | 00/00 a 00/00 | Responsividade, Testes e Manual do Usuário | [Acessar](./docs/sprint3) | [Assistir](#) | 📅 Planejado |

---

<br>
<p align="right"><a href="#topo">↑ Voltar ao topo</a></p>

## 🛠️ Tecnologias Utilizadas <a id="tecnologias"></a>

Para atender aos requisitos técnicos (RN.P) do desafio Radar Cidadão, utilizamos as seguintes ferramentas:

* **Análise de Dados:** [Google Colab](https://colab.research.google.com/) (Pandas/Matplotlib)
* **Linguagem:** [Python 3.10+](https://www.python.org/)
* **Framework Web:** [Flask](https://flask.palletsprojects.com/)
* **Banco de Dados:** [MariaDB/MySQL](https://mariadb.org/) (Sem uso de ORM)
* **Interface:** HTML5 e CSS3 (Design Responsivo)
* **Versionamento:** [GitHub](https://github.com/) (GitHub Flow)

---

## 📂 Estrutura do Projeto <a id="estrutura"></a>

```text
Ainda precisa ser feita
```

<br>
<p align="right"><a href="#topo">↑ Voltar ao topo</a></p>

## ⚙️ Como Executar, Usar e Testar <a id="execucao"></a>

Siga os passos abaixo para configurar o ambiente e executar a aplicação localmente.

### 1. Pré-requisitos
* **Python 3.10 ou superior** instalado.
* **MariaDB/MySQL** instalado e em execução.
* **Google Colab** (apenas para a etapa de análise e limpeza de dados).

### 2. Instalação e Execução (Provisório)
```bash
# 1. Clone o repositório
git clone https://github.com/APILumina/API1_DSM_Lumina.git

# 2. Acesse o diretório
cd API1_DSM_Lumina

# 3. Crie um ambiente virtual
python -m venv venv

# 4. Ative o ambiente virtual
# No Windows:
venv\Scripts\activate

# 5. Instale as dependências
pip install -r requirements.txt

# 6. Execute a aplicação
python src/app.py
```

<br>
<p align="right"><a href="#topo">↑ Voltar ao topo</a></p>

## 👥 Equipe <a id="equipe"></a>
| Função | Nome | GitHub |
| :----: | :--: | :----: |
| Product Owner | Daiane Karine da Silva | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Dai4ne) |
| Scrum Master | Kelwin Felipe Rocha Silva | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/kersilva) |
| Dev Team | Cid Daniel Neves D' Oliveira | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/C1dneve) |
| Dev Team | Guilherme de Siqueira Marques | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/introspective616) |
| Dev Team | Guilherme Henrique Campos Ribeiro  | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/guilherme16092007) |
| Dev Team | Gustavo de Oliveira Azevedo | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/gustaft07) |
| Dev Team | Júlia Carolina dos Santos Inacio | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/juliacarolina728-sudo) |
| Dev Team | Pamela Emily Iwabuchi Maciel | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/pamelaiwabuchi) |
| Dev Team | Vinicius de Souza | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/vinicius538) |


## 🦉 Professores Responsáveis <a id="professores"></a>
| Função | Nome | GitHub |
| :----: | :--: | :----: |
| Professor P2  | Fernando Masanori Ashikaga | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/fmasanori) |
| Professor M2 | Jean Carlos Lourenço Costa | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jeancosta4) |

<br>
<p align="right"><a href="#topo">↑ Voltar ao topo</a></p>
