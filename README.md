# PetCare+
📌 **1. Visão Geral**

O PetCare+ é um sistema web voltado para tutores de animais que desejam organizar e acompanhar a saúde, cuidados e informações dos seus pets. O sistema permite criar contas pessoais, cadastrar vários pets, acompanhar vacinas, histórico de saúde e lembretes, tudo em uma interface simples e intuitiva.

📌 **2. Objetivo do Sistema**

Facilitar o gerenciamento da saúde e rotina dos pets.

Centralizar informações importantes como vacinas, datas, histórico médico e agendamentos.

Fornecer uma interface limpa, moderna e fácil de usar.

Permitir que o usuário cadastre sua conta, faça login e acesse apenas seus próprios pets.

📌 **3. Público-Alvo**

Tutores de animais domésticos.

Clínicas e profissionais que desejam oferecer aos clientes um sistema simples de acompanhamento.

Pessoas que gostam de organizar as informações do pet em um só lugar.

📌 **4. Funcionalidades Principais**
4.1 Cadastro e Autenticação

Criar conta (nome, e-mail, senha).

Login do usuário.

Validação de credenciais.

Sistema inicial utilizando LocalStorage (podendo migrar para banco de dados).

**4.2 Dashboard**

Tela inicial após login.

Exibe:

Boas-vindas com o nome do usuário.

Resumo geral (quantidade de pets, vacinas pendentes, etc.).

Acesso rápido para funcionalidades principais.

**4.3 Gestão de Pets**

Cadastro de pets (nome, idade, raça, peso, foto, observações).

Listagem dos pets cadastrados.

Edição e exclusão de pets.

Visualização individual do pet (perfil do pet).

**4.4 Saúde e Cuidados**

Para cada pet:

Carteira de Vacinação

Registrar vacinas com data e lote.

Marcar vacinas aplicadas.

Lembretes de próximas doses.

Histórico Médico

Consultas.

Exames.

Tratamentos.

Observações do veterinário.

**4.5 Agenda / Lembretes**

Marcar:

Datas de vacina.

Datas de banho ou tosa.

Repetição de medicamentos.

Notificações simples (via tela ou dashboard).

**4.6 Perfil do Usuário**

Editar nome.

Alterar e-mail.

Alterar senha.

Excluir conta.

📌 **5. Tecnologias Utilizadas**
🖥 Front-end

HTML5

CSS3

JavaScript puro

Interface responsiva

Armazenamento local (LocalStorage)

🔧 Back-end (Futuro opcional)

Node.js + Express

Banco: MongoDB ou MySQL

API REST

📌 **6. Estrutura das Telas**

Login

Cadastro de Usuário

Dashboard

Listagem de Pets

Cadastro de Pet

Perfil do Pet

Histórico Médico

Carteira de Vacinação

Agenda / Lembretes

Perfil do Usuário

📌 **7. Fluxo de Usuário**

Usuário acessa o login.

Se não tem conta → vai para cadastro.

Após cadastro, retorna ao login.

Faz login → é direcionado ao dashboard.

No dashboard escolhe:

Cadastrar pet,

Ver pets,

Ver vacinas,

Ver histórico,

Acessar agenda,

Editar perfil.

Pode adicionar e editar informações livremente.

Faz logout quando quiser.

📌 **8. Requisitos Funcionais**

RF01 – Sistema deve permitir criar contas.

RF02 – Sistema deve validar credenciais no login.

RF03 – Usuário pode cadastrar vários pets.

RF04 – Sistema permite registrar vacinas e consultas.

RF05 – Usuário pode editar e excluir informações.

RF06 – Sistema deve proteger o acesso às telas internas.

📌 **9. Requisitos Não-Funcionais**

RNF01 – Interface deve ser responsiva.

RNF02 – Sistema deve ser intuitivo e fácil de navegar.

RNF03 – Login deve carregar em até 3 segundos.

RNF04 – Dados devem ser armazenados de forma segura (LocalStorage ou Banco).

📌 **10. Escalabilidade (Futuro)**

Migração para banco real (MongoDB).

Login com JWT.

Upload real de fotos.

Notificações por e-mail.

App mobile com React Native ou Flutter.
