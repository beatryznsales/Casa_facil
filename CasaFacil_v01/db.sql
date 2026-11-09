CREATE TABLE proprietarios (
	nif INTEGER NOT NULL PRIMARY KEY,
	nome_completo TEXT NOT NULL,
	data_nascimento	TEXT NOT NULL,
	sexo TEXT NOT NULL,
	contacto_telefonico TEXT NOT NULL,
	email	TEXT NOT NULL,
	N_habitacoes_registadas INTEGER NOT NULL   -- alterar, onde o proprio codigo conta o numero de habitações antes de o apresentar
	);

INSERT INTO proprietarios VALUES
(115555889, "Andreia Zeiss", "1945-06-30", "F", "+351912345678", "a.zeiss@gmail.com", 4),
(155888870, "Beatriz Xavier", "1955-11-25", "F", "+351961234567", "beatriz.xavier@gmail.com", 2),
(248516973, "Carlos Umberto", "1983-05-15", "M", "+351934567890", "cumberto@hotmail.com", 3),
(267896549, "Daniel Venâncio", "1996-02-04", "O", "+351936789123", "dani_venancio@gmail.com", 1);


CREATE TABLE  inquilinos (
    nif INTEGER NOT NULL PRIMARY KEY,
	nome_completo TEXT NOT NULL,
	data_nascimento TEXT NOT NULL,
	sexo TEXT NOT NULL,
	contacto_telefonico TEXT NOT NULL,
	email TEXT NOT NULL,
	ordenado_mensal NUMERIC
);

INSERT INTO inquilinos (nif, nome_completo, data_nascimento, sexo, contacto_telefonico, email, ordenado_mensal) VALUES
(102938474, "António José Seguro", "1962-03-11", "M", "+351911223344", "aj.seguro@presidencia.pt", 8500.00),
(219283745, "Luís Montenegro", "1973-02-16", "M", "+351966554433", "l.montenegro@pm.gov.pt", 6500.00),
(123456789, "Marcelo Rebelo de Sousa", "1948-12-12", "M", "+351933445566", "marcelo@professor.pt", 4500.00),
(192837460, "António Costa", "1961-07-17", "M", "+351936889911", "antonio.costa@europa.eu", 7800.00),
(283746513, "André Ventura", "1983-01-03", "M", "+351919876543", "andre.ventura@parlamento.pt", 4000.00),
(246813571, "Catarina Martins", "1973-09-07", "F", "+351961592648", "catarina.martins@bloco.pt", 3800.00),
(399887768, "Donald Trump", "1946-06-14", "M", "+351935416387", "the_donald@whitehouse.gov", 25000.00),
(211335576, "Angela Merkel", "1954-07-17", "F", "+351931112223", "a.merkel@bundestag.de", 15000.00);


CREATE TABLE moradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rua TEXT NOT NULL,
    num_porta TEXT NOT NULL,
    num_apartamento TEXT,
    codigo_postal TEXT NOT NULL,
    cidade TEXT NOT NULL
);


INSERT INTO moradas (rua, num_porta, num_apartamento, codigo_postal, cidade) VALUES
("Rua do Ouro", "34", "2E", "4000-300", "Porto"),
("Rua dos Pinheiros", "800", null, "2750-120", "Cascais"),
("Avenida Central", "3456", null, "4710-229", "Porto"),
("Rua Manuel Luis Nogueira", "55", "4B", "4050-163", "Aveiro"),
("Travessa da Pisca", "908", null, "3450-300", "Lisboa"),
("Rua de Santa Catarina", "200", "1º", "4000-447", "Porto"),
("Avenida da Liberdade", "120", "3Dto", "1250-143", "Lisboa"),
("Praça do Comercio", "10", null, "1100-148", "Lisboa"),
("Rua da Boavista", "45", "2A", "4050-107", "Porto"),
("Rua 31 de Janeiro", "88", null, "4000-542", "Porto");
 
CREATE TABLE imoveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    quartos INTEGER NOT NULL,
    id_morada INTEGER NOT NULL,
    estado TEXT NOT NULL,
    renda NUMERIC NOT NULL,
    duracao TEXT NOT NULL,
    situacao TEXT NOT NULL,
    nif_proprietario	INTEGER NOT NULL,
	nif_inquilino INTEGER,
	FOREIGN KEY (id_morada) REFERENCES moradas(id),
	FOREIGN KEY (nif_proprietario) REFERENCES proprietarios(nif)
	FOREIGN KEY (nif_inquilino) REFERENCES inquilinos(nif)
);

INSERT INTO imoveis (tipo, quartos, id_morada, estado, renda, duracao, situacao, nif_proprietario, nif_inquilino) VALUES
("Apartamento", 2, 1, "Usada", 550.00, "6 meses", "Arrendada", 115555889,102938474),
("Apartamento", 3, 2, "Mau Estado", 400.00, "1 ano", "Arrendada", 155888870, 219283745),
("Apartamento", 1, 3, "Usada", 900.00, "1 ano", "Disponível", 115555889, null),
("Apartamento", 2, 4, "Nova", 2500.00, "3 anos", "Arrendada", 155888870, 123456789),
("Apartamento", 3, 5, "Usada", 1500.00, "1 ano", "Arrendada", 115555889, 192837460),
("Apartamento", 4, 6, "Usada", 750.00, "6 meses", "Disponível", 248516973, null),
("Moradia",5,7, "Nova", 1900.00, "3 anos", "Arrendada", 248516973, 283746513),
("Moradia", 3, 8, "Usada", 2500.00, "5 anos", "Arrendada", 115555889, 246813571),
("Apartamento", 1, 9, "Nova", 800.00, "1 ano", "Arrendada", 248516973, 399887768),
("Quinta", 6, 10,"Mau estado", 3000.00, "5 anos", "Arrendada", 267896549, 211335576);
