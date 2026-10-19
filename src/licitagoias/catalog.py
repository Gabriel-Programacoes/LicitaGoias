"""Biblioteca controlada de produtos e serviços do LicitaGoias.

IDs são estáveis e persistidos nos perfis. Os termos de correspondência são
mantidos pelo produto, não editáveis por cada usuário.
"""
from __future__ import annotations

import json
from pathlib import Path


def _item(item_id: str, kind: str, group: str, name: str, *terms: str) -> dict:
    return {"id": item_id, "kind": kind, "group": group, "name": name,
            "terms": tuple(dict.fromkeys((name, *terms)))}


CATALOG_ITEMS = (
    _item("computadores", "Produto", "Informática e tecnologia", "Computadores e notebooks", "computador", "computadores", "desktop", "notebook", "notebooks", "laptop", "microcomputador", "microcomputadores", "estação de trabalho"),
    _item("impressoras", "Produto", "Informática e tecnologia", "Impressoras e scanners", "impressora", "impressoras", "scanner", "scanners", "multifuncional", "multifuncionais", "toner", "cartucho de tinta"),
    _item("componentes_informatica", "Produto", "Informática e tecnologia", "Peças e componentes de informática", "componente de computador", "peças de computador", "memória ram", "disco rígido", "ssd", "placa-mãe", "processador"),
    _item("redes", "Produto", "Informática e tecnologia", "Redes e conectividade", "equipamento de rede", "roteador", "switch de rede", "ponto de acesso", "access point", "cabeamento de rede", "fibra óptica"),
    _item("telefonia", "Produto", "Informática e tecnologia", "Telefonia e comunicação", "telefone", "telefones", "aparelho celular", "smartphone", "celular", "central telefônica"),
    _item("software", "Produto", "Informática e tecnologia", "Licenças e programas de computador", "software", "licença de software", "licenciamento de software", "sistema informatizado", "programa de computador"),
    _item("seguranca_eletronica", "Produto", "Informática e tecnologia", "Câmeras e segurança eletrônica", "câmera de segurança", "câmeras", "cftv", "alarme", "controle de acesso", "circuito fechado de televisão"),
    _item("material_escritorio", "Produto", "Escritório e mobiliário", "Material de escritório e papelaria", "material de escritório", "papelaria", "papel sulfite", "caneta", "pastas", "material de expediente"),
    _item("mobiliario", "Produto", "Escritório e mobiliário", "Móveis e mobiliário", "mobiliário", "móveis", "mesa", "cadeira", "armário", "estante", "carteira escolar"),
    _item("limpeza", "Produto", "Limpeza e higiene", "Produtos de limpeza e higiene", "material de limpeza", "produto de limpeza", "detergente", "desinfetante", "sabonete", "papel higiênico", "higiene pessoal"),
    _item("descartaveis", "Produto", "Limpeza e higiene", "Descartáveis e acondicionamento", "copo descartável", "saco de lixo", "embalagem descartável", "papel toalha", "máscara descartável"),
    _item("alimentos", "Produto", "Alimentos e bebidas", "Alimentos e gêneros alimentícios", "gêneros alimentícios", "alimento", "alimentos", "cesta básica", "arroz", "feijão", "merenda escolar"),
    _item("agua_bebidas", "Produto", "Alimentos e bebidas", "Água e bebidas", "água mineral", "água potável", "bebida", "bebidas", "suco", "café", "leite"),
    _item("medicamentos", "Produto", "Saúde e laboratório", "Medicamentos e fármacos", "medicamento", "medicamentos", "fármaco", "fármacos", "remédio", "insumo farmacêutico"),
    _item("material_medico", "Produto", "Saúde e laboratório", "Materiais médico-hospitalares", "material hospitalar", "material médico", "luva cirúrgica", "seringa", "gaze", "cateter", "insumo hospitalar"),
    _item("equipamentos_medicos", "Produto", "Saúde e laboratório", "Equipamentos médicos e odontológicos", "equipamento médico", "equipamento hospitalar", "equipamento odontológico", "aparelho médico", "autoclave", "monitor multiparamétrico"),
    _item("laboratorio", "Produto", "Saúde e laboratório", "Materiais e equipamentos de laboratório", "material de laboratório", "reagente", "reagentes", "vidraria laboratorial", "equipamento laboratorial"),
    _item("uniformes", "Produto", "Proteção e vestuário", "Uniformes e vestuário profissional", "uniforme", "uniformes", "roupa profissional", "calçado de segurança", "jaleco", "fardamento"),
    _item("epis", "Produto", "Proteção e vestuário", "Equipamentos de proteção individual", "epi", "equipamento de proteção individual", "capacete de segurança", "botina de segurança", "óculos de proteção", "protetor auricular"),
    _item("veiculos", "Produto", "Veículos e máquinas", "Veículos e automóveis", "veículo", "veículos", "automóvel", "automóveis", "carro", "caminhão", "ônibus", "motocicleta"),
    _item("autopecas", "Produto", "Veículos e máquinas", "Peças e acessórios para veículos", "autopeças", "peça automotiva", "pneu", "bateria automotiva", "peças para veículos"),
    _item("combustiveis", "Produto", "Veículos e máquinas", "Combustíveis e lubrificantes", "combustível", "combustíveis", "gasolina", "diesel", "etanol", "óleo lubrificante"),
    _item("maquinas", "Produto", "Veículos e máquinas", "Máquinas e equipamentos", "máquina", "máquinas", "equipamento industrial", "gerador de energia", "motobomba", "trator"),
    _item("ferramentas", "Produto", "Construção e manutenção", "Ferramentas e equipamentos de oficina", "ferramenta", "ferramentas", "furadeira", "parafusadeira", "serra elétrica", "ferramenta manual"),
    _item("material_construcao", "Produto", "Construção e manutenção", "Materiais de construção", "material de construção", "cimento", "areia", "tijolo", "telha", "tinta", "material de obra"),
    _item("material_eletrico", "Produto", "Construção e manutenção", "Materiais elétricos e iluminação", "material elétrico", "lâmpada", "luminária", "cabo elétrico", "disjuntor", "quadro elétrico"),
    _item("material_hidraulico", "Produto", "Construção e manutenção", "Materiais hidráulicos", "material hidráulico", "tubo pvc", "conexão hidráulica", "torneira", "válvula", "bomba d'água"),
    _item("ar_condicionado", "Produto", "Construção e manutenção", "Ar-condicionado e refrigeração", "ar condicionado", "condicionador de ar", "refrigerador", "freezer", "bebedouro", "ventilador"),
    _item("energia_solar", "Produto", "Construção e manutenção", "Equipamentos de energia solar", "painel solar", "módulo fotovoltaico", "energia fotovoltaica", "inversor solar"),
    _item("agricultura", "Produto", "Agropecuária", "Insumos e equipamentos agrícolas", "insumo agrícola", "implemento agrícola", "semente", "fertilizante", "adubo", "defensivo agrícola"),
    _item("veterinaria", "Produto", "Agropecuária", "Produtos veterinários e animais", "produto veterinário", "medicamento veterinário", "ração animal", "insumo veterinário"),
    _item("livros", "Produto", "Educação e esporte", "Livros e materiais didáticos", "livro", "livros", "material didático", "material pedagógico", "apostila", "publicação"),
    _item("esportes", "Produto", "Educação e esporte", "Materiais esportivos e recreativos", "material esportivo", "equipamento esportivo", "bola", "uniforme esportivo", "brinquedo", "parquinho"),
    _item("sinalizacao", "Produto", "Infraestrutura e sinalização", "Placas e sinalização", "placa de sinalização", "sinalização viária", "placa de trânsito", "sinalização de segurança"),
    _item("equipamentos_audio", "Produto", "Infraestrutura e sinalização", "Equipamentos de áudio e vídeo", "equipamento audiovisual", "projetor", "televisor", "microfone", "caixa de som", "mesa de som"),
    _item("software_desenvolvimento", "Serviço", "Tecnologia da informação", "Desenvolvimento e manutenção de sistemas", "desenvolvimento de software", "desenvolvimento de sistema", "fábrica de software", "manutenção de sistema", "programação"),
    _item("suporte_ti", "Serviço", "Tecnologia da informação", "Suporte técnico em informática", "suporte técnico", "suporte de informática", "help desk", "service desk", "manutenção de computadores", "assistência técnica de informática"),
    _item("infra_ti", "Serviço", "Tecnologia da informação", "Infraestrutura, nuvem e segurança digital", "serviço de nuvem", "computação em nuvem", "hospedagem de sistema", "segurança da informação", "cibersegurança", "backup de dados"),
    _item("internet", "Serviço", "Tecnologia da informação", "Internet e telecomunicações", "acesso à internet", "link de internet", "conexão de internet", "telecomunicação", "transmissão de dados"),
    _item("consultoria_ti", "Serviço", "Tecnologia da informação", "Consultoria em tecnologia", "consultoria de ti", "consultoria em informática", "planejamento de tecnologia", "governança de ti"),
    _item("engenharia", "Serviço", "Engenharia e construção", "Serviços de engenharia", "serviço de engenharia", "projeto de engenharia", "fiscalização de obra", "laudo de engenharia"),
    _item("arquitetura", "Serviço", "Engenharia e construção", "Arquitetura e projetos", "serviço de arquitetura", "projeto arquitetônico", "projeto de arquitetura", "urbanismo"),
    _item("obras", "Serviço", "Engenharia e construção", "Obras e reformas", "obra de construção", "construção civil", "reforma predial", "ampliação de prédio", "execução de obra"),
    _item("manutencao_predial", "Serviço", "Engenharia e construção", "Manutenção predial", "manutenção de edifício", "manutenção de prédio", "reparo predial", "conservação predial"),
    _item("manutencao_eletrica", "Serviço", "Engenharia e construção", "Instalação e manutenção elétrica", "manutenção elétrica", "instalação elétrica", "serviço elétrico", "reparo elétrico"),
    _item("manutencao_hidraulica", "Serviço", "Engenharia e construção", "Instalação e manutenção hidráulica", "manutenção hidráulica", "instalação hidráulica", "serviço hidráulico", "reparo hidráulico"),
    _item("climatizacao", "Serviço", "Engenharia e construção", "Instalação e manutenção de ar-condicionado", "manutenção de ar condicionado", "instalação de ar condicionado", "manutenção de refrigeração", "climatização"),
    _item("limpeza_conservacao", "Serviço", "Serviços operacionais", "Limpeza e conservação de ambientes", "serviço de limpeza", "limpeza predial", "limpeza e conservação", "asseio e conservação"),
    _item("vigilancia", "Serviço", "Serviços operacionais", "Vigilância e segurança patrimonial", "serviço de vigilância", "vigilância patrimonial", "segurança patrimonial", "portaria", "controle de acesso"),
    _item("dedetizacao", "Serviço", "Serviços operacionais", "Dedetização e controle de pragas", "dedetização", "desinsetização", "controle de pragas", "desratização"),
    _item("residuos", "Serviço", "Serviços operacionais", "Coleta e gestão de resíduos", "coleta de resíduos", "coleta de lixo", "gestão de resíduos", "destinação de resíduos", "limpeza urbana"),
    _item("transporte_pessoas", "Serviço", "Transporte e logística", "Transporte de passageiros", "transporte de pessoas", "transporte escolar", "transporte de passageiros", "locação de ônibus"),
    _item("transporte_cargas", "Serviço", "Transporte e logística", "Transporte de cargas e frete", "transporte de carga", "frete", "serviço de transporte de mercadoria", "logística de cargas"),
    _item("manutencao_veiculos", "Serviço", "Transporte e logística", "Manutenção de veículos", "manutenção automotiva", "oficina mecânica", "serviço de mecânica", "reparo de veículos"),
    _item("locacao_veiculos", "Serviço", "Transporte e logística", "Locação de veículos", "aluguel de veículos", "locação de automóvel", "locação de caminhão", "locação de máquinas"),
    _item("contabilidade", "Serviço", "Gestão e assessoria", "Serviços contábeis", "contabilidade", "serviço de contabilidade", "assessoria contábil", "auditoria contábil"),
    _item("juridico", "Serviço", "Gestão e assessoria", "Assessoria e serviços jurídicos", "serviço jurídico", "assessoria jurídica", "consultoria jurídica", "advocacia"),
    _item("consultoria_gestao", "Serviço", "Gestão e assessoria", "Consultoria em gestão", "consultoria empresarial", "consultoria administrativa", "planejamento estratégico", "gestão organizacional"),
    _item("servicos_administrativos", "Serviço", "Gestão e assessoria", "Apoio administrativo", "serviço administrativo", "apoio administrativo", "serviços auxiliares", "terceirização administrativa"),
    _item("treinamento", "Serviço", "Educação e capacitação", "Cursos e capacitação profissional", "treinamento profissional", "curso de capacitação", "capacitação de servidores", "formação profissional"),
    _item("educacao", "Serviço", "Educação e capacitação", "Serviços educacionais", "serviço educacional", "consultoria educacional", "formação educacional", "avaliação educacional"),
    _item("saude", "Serviço", "Saúde", "Serviços de saúde e atendimento médico", "serviço médico", "atendimento médico", "serviço de saúde", "consulta médica", "atendimento ambulatorial"),
    _item("exames", "Serviço", "Saúde", "Exames e análises clínicas", "exame laboratorial", "análise clínica", "serviço de laboratório", "diagnóstico por imagem", "exames médicos"),
    _item("alimentacao_coletiva", "Serviço", "Alimentação e eventos", "Fornecimento de refeições", "fornecimento de alimentação", "refeição pronta", "alimentação coletiva", "merenda escolar", "serviço de cozinha"),
    _item("marketing", "Serviço", "Comunicação e eventos", "Publicidade e comunicação", "serviço de publicidade", "agência de publicidade", "campanha publicitária", "comunicação institucional", "marketing"),
    _item("impressao", "Serviço", "Comunicação e eventos", "Impressão e serviços gráficos", "serviço gráfico", "impressão gráfica", "impressão de material", "confecção de impressos", "plotagem"),
    _item("eventos", "Serviço", "Comunicação e eventos", "Organização de eventos", "organização de evento", "produção de eventos", "serviço de eventos", "sonorização de evento"),
    _item("audiovisual", "Serviço", "Comunicação e eventos", "Produção audiovisual e fotografia", "produção audiovisual", "filmagem", "fotografia", "edição de vídeo", "transmissão ao vivo"),
    _item("projetos_ambientais", "Serviço", "Meio ambiente e campo", "Serviços ambientais", "consultoria ambiental", "licenciamento ambiental", "estudo ambiental", "monitoramento ambiental"),
    _item("servicos_agricolas", "Serviço", "Meio ambiente e campo", "Serviços agrícolas", "serviço agrícola", "preparo de solo", "manutenção de área verde", "jardinagem", "paisagismo"),
    _item("servicos_veterinarios", "Serviço", "Meio ambiente e campo", "Serviços veterinários", "atendimento veterinário", "serviço veterinário", "castração de animais", "controle de zoonoses"),
)

CATALOG_BY_ID = {item["id"]: item for item in CATALOG_ITEMS}

_MUNICIPALITY_DATA = json.loads(
    (Path(__file__).parent / "api" / "static" / "municipalities-go.json").read_text(encoding="utf-8")
)
MUNICIPALITIES = {
    str(item["id"]): {"name": item["name"], "terms": (item["name"],)}
    for item in _MUNICIPALITY_DATA
}

MODALITIES = {
    "1": {"name": "Leilão · eletrônico", "terms": ("leilao", "eletronico")},
    "2": {"name": "Diálogo competitivo", "terms": ("dialogo competitivo",)},
    "3": {"name": "Concurso", "terms": ("concurso",)},
    "4": {"name": "Concorrência · eletrônica", "terms": ("concorrencia", "eletronica")},
    "5": {"name": "Concorrência · presencial", "terms": ("concorrencia", "presencial")},
    "6": {"name": "Pregão · eletrônico", "terms": ("pregao", "eletronico")},
    "7": {"name": "Pregão · presencial", "terms": ("pregao", "presencial")},
    "8": {"name": "Dispensa de licitação", "terms": ("dispensa",)},
    "9": {"name": "Inexigibilidade", "terms": ("inexigibilidade",)},
    "10": {"name": "Manifestação de interesse", "terms": ("manifestacao de interesse",)},
    "11": {"name": "Pré-qualificação", "terms": ("pre qualificacao", "pre-qualificacao")},
    "12": {"name": "Credenciamento", "terms": ("credenciamento",)},
    "13": {"name": "Leilão · presencial", "terms": ("leilao", "presencial")},
    "14": {"name": "Inaplicabilidade da licitação", "terms": ("inaplicabilidade",)},
}

# Classification happens at the notice/opportunity level. These are controlled
# business areas; terms are matched against the published object and its
# complementary information, never against notice line items.
OPPORTUNITY_CATEGORIES = {
    "construction_materials": {
        "name": "Material de construção",
        "description": "Materiais, insumos e acabamentos para obras.",
        "terms": (
            "material de construção", "materiais de construção", "material de obra",
            "insumos para construção", "cimento", "argamassa", "areia lavada",
            "brita", "tijolo", "bloco de concreto", "telha", "piso cerâmico",
            "revestimento cerâmico", "tinta predial", "tinta acrílica",
            "material elétrico", "material hidráulico", "tubo pvc", "conexão hidráulica",
            "louça sanitária", "ferro para construção", "aço para construção",
            "madeira para construção", "material de acabamento",
        ),
    },
    "construction_services": {
        "name": "Obras, engenharia e reformas",
        "description": "Execução de obras, projetos e manutenção predial.",
        "terms": (
            "obra civil", "obras civis", "construção civil", "execução de obra",
            "reforma predial", "reforma de prédio", "ampliação de prédio",
            "manutenção predial", "serviço de engenharia", "projeto de engenharia",
            "fiscalização de obra", "projeto arquitetônico", "serviço de arquitetura",
        ),
    },
    "it_and_technology": {
        "name": "Informática e tecnologia",
        "description": "Equipamentos, sistemas, suporte e infraestrutura de TI.",
        "terms": (
            "equipamento de informática", "computador", "notebook", "impressora",
            "servidor de rede", "licença de software", "licenciamento de software",
            "desenvolvimento de sistema", "suporte técnico em informática",
            "serviço de nuvem", "segurança da informação", "link de internet",
        ),
    },
    "vehicles_and_fleet": {
        "name": "Veículos e frota",
        "description": "Aquisição, locação, manutenção e abastecimento de veículos.",
        "terms": (
            "aquisição de veículo", "aquisição de veículos", "veículo automotor",
            "veículo de passeio", "automóvel de passeio", "carro de passeio",
            "caminhão", "ônibus", "motocicleta", "locação de veículos",
            "manutenção de veículos", "peças para veículos", "combustível para frota",
        ),
    },
    "health_and_medical": {
        "name": "Saúde e materiais médicos",
        "description": "Serviços de saúde, medicamentos e materiais hospitalares.",
        "terms": (
            "serviço de saúde", "atendimento médico", "serviço médico",
            "material médico hospitalar", "material hospitalar", "medicamento",
            "insumo farmacêutico", "equipamento hospitalar", "exame laboratorial",
        ),
    },
    "food_and_meals": {
        "name": "Alimentos e refeições",
        "description": "Gêneros alimentícios, merenda e alimentação preparada.",
        "terms": (
            "gêneros alimentícios", "aquisição de alimentos", "cesta básica",
            "merenda escolar", "fornecimento de refeições", "alimentação coletiva",
            "fornecimento de alimentação", "água mineral", "refeição pronta",
        ),
    },
    "cleaning_and_hygiene": {
        "name": "Limpeza e higiene",
        "description": "Produtos de higiene, limpeza e conservação de ambientes.",
        "terms": (
            "material de limpeza", "produtos de limpeza", "produto de higiene",
            "papel higiênico", "serviço de limpeza", "limpeza e conservação",
            "asseio e conservação", "limpeza predial", "coleta de resíduos",
        ),
    },
    "office_and_furniture": {
        "name": "Escritório e mobiliário",
        "description": "Móveis, material de expediente e papelaria.",
        "terms": (
            "mobiliário", "móveis para escritório", "mobiliário escolar",
            "material de escritório", "material de expediente", "material de papelaria",
            "papel sulfite", "cadeira de escritório", "mesa de escritório",
        ),
    },
    "security_and_protection": {
        "name": "Segurança e proteção",
        "description": "Vigilância, segurança eletrônica e equipamentos de proteção.",
        "terms": (
            "serviço de vigilância", "vigilância patrimonial", "segurança patrimonial",
            "câmera de segurança", "sistema de cftv", "controle de acesso",
            "equipamento de proteção individual", "uniforme profissional",
        ),
    },
    "agriculture_and_animals": {
        "name": "Agropecuária e animais",
        "description": "Insumos e serviços agropecuários e veterinários.",
        "terms": (
            "insumo agrícola", "implemento agrícola", "fertilizante", "defensivo agrícola",
            "serviço agrícola", "serviço veterinário", "medicamento veterinário",
            "ração animal", "castração de animais",
        ),
    },
    "transport_and_logistics": {
        "name": "Transporte e logística",
        "description": "Transporte de pessoas e cargas e serviços logísticos.",
        "terms": (
            "transporte escolar", "transporte de passageiros", "transporte de cargas",
            "serviço de frete", "logística de cargas", "transporte de mercadorias",
        ),
    },
    "administrative_and_consulting": {
        "name": "Gestão, consultoria e serviços administrativos",
        "description": "Consultoria, assessoria, contabilidade e apoio administrativo.",
        "terms": (
            "consultoria empresarial", "consultoria em gestão", "assessoria jurídica",
            "serviços contábeis", "auditoria contábil", "apoio administrativo",
            "serviços administrativos", "terceirização administrativa",
        ),
    },
    "education_and_training": {
        "name": "Educação e capacitação",
        "description": "Serviços educacionais, cursos e materiais didáticos.",
        "terms": (
            "serviço educacional", "curso de capacitação", "treinamento profissional",
            "capacitação de servidores", "material didático", "material pedagógico",
        ),
    },
    "communication_and_events": {
        "name": "Comunicação, gráfica e eventos",
        "description": "Publicidade, impressão, audiovisual e organização de eventos.",
        "terms": (
            "serviço de publicidade", "comunicação institucional", "serviço gráfico",
            "impressão gráfica", "material gráfico", "organização de eventos",
            "produção de eventos", "produção audiovisual", "transmissão ao vivo",
        ),
    },
    "energy_and_climatization": {
        "name": "Energia e climatização",
        "description": "Energia solar, ar-condicionado e sistemas de refrigeração.",
        "terms": (
            "energia fotovoltaica", "painel solar", "sistema de energia solar",
            "instalação de ar condicionado", "manutenção de ar condicionado",
            "serviço de climatização", "manutenção de refrigeração",
        ),
    },
}

STATUSES = {
    "open": {"name": "Recebendo propostas", "terms": ("recebendo proposta", "aberta", "aberto para propostas")},
    "dispute": {"name": "Em disputa ou andamento", "terms": ("em disputa", "em andamento", "lances")},
    "suspended": {"name": "Suspensa", "terms": ("suspensa", "suspenso")},
    "canceled": {"name": "Cancelada ou revogada", "terms": ("cancelada", "cancelado", "revogada", "revogado", "anulada", "anulado")},
    "adjudicated": {"name": "Adjudicada ou homologada", "terms": ("adjudicada", "adjudicado", "homologada", "homologado")},
    "closed": {"name": "Encerrada ou concluída", "terms": ("encerrada", "encerrado", "concluída", "concluído", "finalizada", "finalizado")},
}

DEADLINE_OPTIONS = (None, 7, 15, 30, 60, 90, 180, 365)


def catalog_response() -> dict:
    return {
        "municipalities": [{"id": code, "name": item["name"]} for code, item in MUNICIPALITIES.items()],
        "modalities": [{"id": code, "name": item["name"]} for code, item in MODALITIES.items()],
        "opportunity_categories": [
            {"id": code, "name": item["name"], "description": item["description"]}
            for code, item in OPPORTUNITY_CATEGORIES.items()
        ],
        "statuses": [{"id": code, "name": item["name"]} for code, item in STATUSES.items()],
        "deadline_days": list(DEADLINE_OPTIONS),
    }
