CREATE DATABASE EmpreGO;

USE EmpreGO;

CREATE TABLE Empresa (
    Id_Empresa INT PRIMARY KEY AUTO_INCREMENT,
    Nome_Empresa VARCHAR(100) NOT NULL,
    CNPJ CHAR(14) NOT NULL,
    Telefone CHAR(11) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Senha VARCHAR(30) NOT NULL,
    Status ENUM('Ativa', 'Inativa') DEFAULT 'ativa' NOT NULL
);

CREATE TABLE Vaga (
    Id_Vaga INT PRIMARY KEY AUTO_INCREMENT,
    Titulo VARCHAR(100) NOT NULL,
    Descricao TEXT NOT NULL,
    Formato ENUM('Presencial', 'Híbrido', 'Remoto') NOT NULL,
    Tipo ENUM('CLT', 'PJ') NOT NULL,
    Local VARCHAR(100),
    Salario VARCHAR(10), 
    Id_Empresa INT NOT NULL,
    Status ENUM('Ativa', 'Inativa') DEFAULT 'Ativa' NOT NULL,
    FOREIGN KEY (Id_Empresa) REFERENCES Empresa (Id_Empresa)
);

CREATE TABLE candidato (
    id_candidato INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone CHAR(11) NOT NULL,
    curriculo VARCHAR(50) NOT NULL,
    id_vaga INT,
    FOREIGN KEY (id_vaga) REFERENCES Vaga (Id_Vaga)
);

INSERT INTO empresa (nome_empresa, cnpj, telefone, email, senha, status)
VALUES
('Tech Solutions', '12345678000199', '11987654321', 'contato@techsolutions.com.br', 'senha123', 'ativa'),
('Innova Consulting', '98765432000177', '21987654321', 'info@innovaconsulting.com', 'senha456', 'ativa'),
('Future Devs', '45678912000188', '31987654321', 'hr@futuredevs.com', 'senha789', 'ativa');

INSERT INTO vaga (titulo, descricao, formato, tipo, local, salario, id_empresa, status)
VALUES
('Desenvolvedor Frontend', 'Desenvolvimento de interfaces web com foco em usabilidade e performance.', 'Remoto', 'CLT', 'Remoto', 'R$ 5000', 1, 'ativa'),
('Desenvolvedor Backend', 'Implementação de APIs e manutenção de servidores.', 'Híbrido', 'CLT', 'São Paulo - SP', 'R$ 6000', 1, 'ativa'),
('Analista de Dados', 'Análise de grandes volumes de dados e geração de relatórios.', 'Presencial', 'CLT', 'São Paulo - SP', 'R$ 5500', 1, 'ativa'),
('Gerente de Projetos', 'Gestão de equipes e acompanhamento de cronogramas.', 'Híbrido', 'PJ', 'São Paulo - SP', 'R$ 8000', 1, 'ativa'),
('Designer UX/UI', 'Criação de interfaces intuitivas e focadas na experiência do usuário.', 'Remoto', 'PJ', 'Remoto', 'R$ 4500', 1, 'ativa');


INSERT INTO vaga (titulo, descricao, formato, tipo, local, salario, id_empresa, status)
VALUES
('Consultor de TI', 'Consultoria em infraestrutura e suporte técnico.', 'Presencial', 'CLT', 'Rio de Janeiro - RJ', 'R$ 7000', 2, 'ativa'),
('Especialista em Segurança da Informação', 'Responsável por garantir a segurança dos dados e infraestrutura.', 'Híbrido', 'CLT', 'Rio de Janeiro - RJ', 'R$ 9000', 2, 'ativa'),
('DevOps Engineer', 'Automatização de processos e gestão de infraestrutura em nuvem.', 'Remoto', 'PJ', 'Remoto', 'R$ 8500', 2, 'ativa'),
('Scrum Master', 'Facilitação de equipes ágeis utilizando Scrum.', 'Remoto', 'PJ', 'Remoto', 'R$ 7000', 2, 'ativa'),
('Analista de Sistemas', 'Análise e desenvolvimento de sistemas corporativos.', 'Presencial', 'CLT', 'Rio de Janeiro - RJ', 'R$ 6000', 2, 'ativa');


INSERT INTO vaga (titulo, descricao, formato, tipo, local, salario, id_empresa, status)
VALUES
('Programador Fullstack', 'Desenvolvimento de soluções completas, frontend e backend.', 'Híbrido', 'CLT', 'Belo Horizonte - MG', 'R$ 7000', 3, 'ativa'),
('Engenheiro de Software', 'Desenvolvimento de software e gestão de ciclo de vida de aplicações.', 'Presencial', 'CLT', 'Belo Horizonte - MG', 'R$ 9000', 3, 'ativa'),
('QA Tester', 'Testes automatizados e garantia de qualidade do software.', 'Remoto', 'CLT', 'Remoto', 'R$ 6000', 3, 'ativa'),
('Arquiteto de Soluções', 'Definição de arquitetura de sistemas e infraestrutura.', 'Híbrido', 'PJ', 'Belo Horizonte - MG', 'R$ 10000', 3, 'ativa'),
('Analista de Suporte', 'Atendimento a clientes e suporte técnico de sistemas.', 'Presencial', 'CLT', 'Belo Horizonte - MG', 'R$ 4000', 3, 'ativa');
