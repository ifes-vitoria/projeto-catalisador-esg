from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import numpy as np

class Pergunta(BaseModel):
    nivel: int
    name: str
    resposta: str
    eixo: str
    tema: str
    criterio: str

    @classmethod
    def validate_resposta(cls, resposta: str) -> str:
        if "sim" in resposta.lower().strip():
            return "0"
        elif "não" in resposta.lower().strip():
            return "1"
        elif "não aplicado" in resposta.lower().strip():
            return "2"
        return resposta

    @classmethod
    def from_dict(cls, data: Dict[str, Union[int, str]]) -> "Pergunta":
        return cls(
            nivel=int(data.get("nivel")),
            name=data.get("name"),
            resposta=cls.validate_resposta(data.get("resposta")),
            eixo=data.get("eixo").lower().replace('ç', 'c').strip(),
            tema=data.get("tema"),
            criterio=data.get("criterio"),
        )

class Indicador(BaseModel):
    eixo: str
    item: str
    valor: float

    @classmethod
    def from_dict(cls, data: Dict[str, Union[float, str]]) -> "Indicador":
        return cls(
            eixo=data.get("eixo").lower(),
            item=data.get("item"),
            valor=float(data.get("valor")),
        )

    @classmethod
    def from_indicator_dict(
        cls, data: Dict[str, Union[float, str]], eixo: str
    ) -> List["Indicador"]:
        return [
            cls.from_dict({"eixo": eixo.lower().replace('ç', 'c').strip(), "item": k, "valor": v})
            for k, v in data.items()
        ]

class Empresa(BaseModel):
    nome_empresa: str
    data: str
    producaomes: str
    localizacao: str
    unidproducao: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Empresa":
        return cls(
            nome_empresa=data.get("nome_empresa"),
            data=data.get("data"),
            localizacao=data.get("localizacao"),
        )

class MaturidadeInformation(BaseModel):
    nivel: int
    color: str
    titulo: str
    descricao: str

class Recomendacao(BaseModel):
    eixo: str
    recomendacoes: List[str]

class MaturityLevel:
    ESTAGIO_1 = (
        "red",
        'Elementar',
        "A organização possui um processo de identificação de atendimento da legislação e restringe-se à abordagem da legislação e requisitos regulamentares (quando pertinente) e/ou trata o tema ou critério de forma incipiente, se não houver requisitos regulamentares obrigatórios.",
    )
    ESTAGIO_2 = (
        "orange",
        'Não Integrado',
        "A organização trata o critério de modo inicial por meio de práticas dispersas, ainda não integradas de modo satisfatório com a gestão.",
    )
    ESTAGIO_3 = (
        "yellow",
        'Gerencial',
        "A partir do estágio 3, a liderança já possui uma atuação mais consciente em relação a temas ESG materiais para seu negócio, indo além da legislação. As práticas possuem enfoque operacional e passam a ser gerenciadas em processos estruturados, com o objetivo de mitigar riscos de imagem, reputação e melhorias em eficiência e qualidade. As organizações aumentam sua visão em relação aos temas ESG, e os líderes têm um envolvimento mais profundo, assumindo o papel de coordenação do tema, ampliando o nível de aprendizado e inovação corporativa. Neste contexto, se inicia a aderência ao que chamamos de práticas ESG.",
    )
    ESTAGIO_4 = (
        "green",
        'Estratégico',
        "A organização trata o critério, entendendo os riscos e seus impactos positivos (oportunidades) e negativos (ameaças) relacionados ao negócio (incluindo a cadeia de valor), considerando-os na tomada de decisão estratégica. A organização contribui com soluções para os desafios ESG pela diferenciação de produtos e serviços. A organização estabelece objetivos e metas, e comunica os seus resultados. A organização promove inovação tecnológica ou novos modelos de negócio que viabilizem novas abordagens sobre o tema em questão, maximizando a agregação de valor para o negócio. A organização promove o engajamento das partes interessadas, compreendendo suas expectativas e necessidades, de modo a gerar impactos sociais e ambientais positivos dentro do conceito de valor compartilhado.",
    )
    ESTAGIO_5 = (
        "blue",
        'Transformador',
        "A organização já posicionou o ESG como base de seu modelo estratégico de negócio, e atua para impactar e influenciar outras organizações no fortalecimento dessa pauta, em um movimento mais amplo frente ao seu setor de atividade e cadeias de valor. O trabalho de impacto e influência é uma disciplina contínua e evolutiva. A organização passa por transformações para gerar valor compartilhado e trata o critério de forma a influenciar e catalisar mudanças transformacionais que fortaleçam a pauta ESG em um cenário mais amplo. A organização promove engajamento estruturado com as partes interessadas e grupos impactados neste tema, buscando a superação conjunta das metas estabelecidas e a maximização dos impactos positivos sociais e ambientais. A organização apresenta liderança, buscando protagonismo frente ao seu setor de atividade e cadeias de valor, realizando, de forma sistemática, a defesa do tema com a sociedade, de modo mais amplo para o estabelecimento de programas privados e políticas públicas estruturantes.",
    )

    @classmethod
    def get_description(cls, level: int) -> MaturidadeInformation:
        level_now = getattr(cls, f"ESTAGIO_{level}")
        return MaturidadeInformation(
            nivel=level, color=level_now[0], titulo=level_now[1], descricao=level_now[2]
        )

class RecommendationLevel:
    ESTAGIO_1 = {
        "ambiental": [
            "Desenvolver um plano de ação para atender aos requisitos ambientais regulatórios.",
            "Implementar práticas básicas de gestão ambiental.",
        ],
        "social": [
            "Iniciar programas de treinamento e desenvolvimento para funcionários.",
            "Estabelecer políticas de diversidade e inclusão.",
        ],
        "governanca": [
            "Aumentar a transparência nas práticas de governança.",
            "Rever e melhorar as políticas de compliance e ética.",
        ],
    }
    ESTAGIO_2 = {
        "ambiental": [
            "Integrar práticas ambientais nas operações diárias.",
            "Desenvolver uma estratégia de gestão ambiental mais estruturada.",
        ],
        "social": [
            "Formalizar e documentar programas de treinamento e desenvolvimento.",
            "Estabelecer metas claras para a diversidade e inclusão.",
        ],
        "governanca": [
            "Melhorar a formação e o treinamento dos membros do conselho.",
            "Estabelecer processos para maior independência e eficácia do conselho.",
        ],
    }
    ESTAGIO_3 = {
        "ambiental": [
            "Implementar sistemas de gestão ambiental integrados.",
            "Realizar avaliações de impacto ambiental periódicas.",
        ],
        "social": [
            "Desenvolver programas de engajamento comunitário.",
            "Estabelecer canais de comunicação interna para feedback dos funcionários.",
        ],
        "governanca": [
            "Integrar políticas de governança com os processos operacionais.",
            "Estabelecer comitês dedicados à gestão de ESG.",
        ],
    }
    ESTAGIO_4 = {
        "ambiental": [
            "Desenvolver e implementar metas ambientais alinhadas à estratégia de negócios.",
            "Adotar tecnologias sustentáveis para otimizar o uso de recursos.",
        ],
        "social": [
            "Estabelecer indicadores de desempenho social e monitorá-los regularmente.",
            "Promover iniciativas de responsabilidade social corporativa alinhadas com a estratégia empresarial.",
        ],
        "governanca": [
            "Integrar ESG na governança corporativa com metas e indicadores claros.",
            "Realizar auditorias de governança para garantir o alinhamento com as práticas estratégicas de ESG.",
        ],
    }
    ESTAGIO_5 = {
        "ambiental": [
            "Liderar iniciativas setoriais de sustentabilidade e promover parcerias estratégicas.",
            "Influenciar políticas públicas ambientais e participar de fóruns internacionais sobre sustentabilidade.",
        ],
        "social": [
            "Desenvolver programas de impacto social de grande escala e influenciar práticas do setor.",
            "Colaborar com ONGs e outras organizações para promover mudanças sociais significativas.",
        ],
        "governanca": [
            "Estabelecer padrões de governança de ESG reconhecidos globalmente.",
            "Atuar como referência em governança de ESG, influenciando outras organizações e o setor como um todo.",
        ],
    }
    
    @classmethod
    def get_description(cls, level: int, eixo: str) -> Recomendacao:
        eixo_now = eixo.lower().replace('ç', 'c').strip()
        level_now: Dict = getattr(cls, f"ESTAGIO_{level}")
        level_now = level_now.get(eixo_now)
        return Recomendacao(eixo=eixo_now, recomendacoes=level_now)

    @classmethod
    def get_all_lvl_description(cls, level: int) -> List[str]:
        level_now: Dict = getattr(cls, f"ESTAGIO_{level}")
        recomendations = []
        for vv in level_now.values():
            recomendations += vv
        return recomendations

class EixoMaturidade(BaseModel):
    eixo: str
    nivel: int
    data: Optional[str] = None
    maturidade: Optional[MaturidadeInformation] = None
    recomendacoes: Optional[Recomendacao] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EixoMaturidade":
        eixo = data.get("eixo")
        nivel = data.get("nivel")
        date = data.get("data", None)
        maturidade = MaturityLevel.get_description(nivel)
        recomendacoes = RecommendationLevel.get_description(nivel, eixo)
        return cls(
            eixo=eixo, nivel=nivel, data=date,
            maturidade=maturidade,
            recomendacoes=recomendacoes
        )

class Data(BaseModel):
    empresa: Empresa
    perguntas: List[Pergunta]
    indicadores: List[Indicador]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        indicadores = [i for i in data.keys() if i.startswith("indicadores")]
        indicadores_objs = []
        for i in indicadores:
            indicadores_objs += Indicador.from_indicator_dict(
                data[i], i.replace("indicadores_", "")
            )
            
        for p in data.get("perguntas"):
            try:
                Pergunta.from_dict(p)
            except Exception as e:
                raise ValueError(f"Erro ao criar pergunta: {e} para {p['name']}")
        
        return cls(
            empresa=Empresa.from_dict(data),
            perguntas=[Pergunta.from_dict(p) for p in data.get("perguntas")],
            indicadores=indicadores_objs,
        )

    # TODO: verificado A lógica esperada: se todas as perguntas do Nível 1 forem respondidas com "Sim" ou "Não Aplicável", a empresa avança para o Nível 2. Esse processo deve continuar sucessivamente até o Nível 5. Caso haja uma pergunta respondida com "Não" em qualquer nível, a empresa é avaliada e permanece nesse nível.
    def get_aspecto_per_eixo(self, add_date=False) -> List[EixoMaturidade]:
        pergunta_df = pd.DataFrame([i.model_dump() for i in self.perguntas])
        pergunta_df['resposta'] = pergunta_df['resposta'].astype(int)
        # resposta -> 0: sim, 1: nao, 2: nao aplicavel
        pergunta_df['answer_yes'] = pergunta_df['resposta'].apply(lambda x: x in [0, 2])
        pergunta_df_max_nivel = pergunta_df[['eixo', 'nivel', 'answer_yes']].groupby(['eixo', 'nivel'], as_index=False).agg({'answer_yes': lambda x: x.sum()/x.count()})
        pergunta_df_max_nivel['answer_all'] = pergunta_df_max_nivel.answer_yes==1.0
        pergunta_df_max_nivel['answer_all'] = pergunta_df_max_nivel[['eixo', 'nivel', 'answer_all']].apply(lambda x: True if x.nivel==1 else x.answer_all, axis=1)
        pergunta_df_max_nivel = pergunta_df_max_nivel[['eixo', 'nivel', 'answer_all']].copy()
        pergunta_df_max_nivel = pergunta_df_max_nivel[pergunta_df_max_nivel.answer_all]
        pergunta_df_max_nivel = pergunta_df_max_nivel.drop(columns=['answer_all']).groupby('eixo', as_index=False).agg(lambda x: x.tolist())
        pergunta_df_max_nivel['cumsum'] = pergunta_df_max_nivel.nivel.apply(lambda x: np.cumsum([i in x for i in range(1, 6)]))
        pergunta_df_max_nivel['cumsum'] = pergunta_df_max_nivel['cumsum'].apply(lambda x: np.where(np.diff(x, 1)==0)[0])
        pergunta_df_max_nivel['nivel'] = pergunta_df_max_nivel['cumsum'].apply(lambda x: (x[0] if len(x) else 4)+1)
        
        cols = ['eixo', 'nivel']
        if add_date:
            pergunta_df_max_nivel['data'] = self.empresa.data
            cols += ['data']
        eixo_maturidade_list = pergunta_df_max_nivel[cols].to_dict('records')
        
        return [EixoMaturidade.from_dict(i) for i in eixo_maturidade_list]

    def get_aspecto_per_eixo_and_tema(self, add_date=False) -> List[EixoMaturidade]:
        pergunta_df = pd.DataFrame([i.model_dump() for i in self.perguntas])
        pergunta_df['resposta'] = pergunta_df['resposta'].astype(int)
        pergunta_df['answer_yes'] = pergunta_df['resposta'].apply(lambda x: x in [0, 2])
        pergunta_df_max_nivel = pergunta_df[['eixo', 'tema', 'nivel', 'answer_yes']].groupby(['eixo', 'tema', 'nivel'], as_index=False).agg({'answer_yes': lambda x: x.sum()/x.count()})
        pergunta_df_max_nivel['answer_all'] = pergunta_df_max_nivel.answer_yes==1.0
        pergunta_df_max_nivel['answer_all'] = pergunta_df_max_nivel[['eixo', 'nivel', 'tema', 'answer_all']].apply(lambda x: True if x.nivel==1 else x.answer_all, axis=1)
        pergunta_df_max_nivel = pergunta_df_max_nivel[['eixo', 'tema', 'nivel', 'answer_all']].copy()
        pergunta_df_max_nivel = pergunta_df_max_nivel[pergunta_df_max_nivel.answer_all]
        pergunta_df_max_nivel = pergunta_df_max_nivel.drop(columns=['answer_all']).groupby(['eixo', 'tema'], as_index=False).agg(lambda x: x.tolist())
        pergunta_df_max_nivel['cumsum'] = pergunta_df_max_nivel.nivel.apply(lambda x: np.cumsum([i in x for i in range(1, 6)]))
        pergunta_df_max_nivel['cumsum'] = pergunta_df_max_nivel['cumsum'].apply(lambda x: np.where(np.diff(x, 1)==0)[0])
        pergunta_df_max_nivel['nivel'] = pergunta_df_max_nivel['cumsum'].apply(lambda x: (x[0] if len(x) else 4)+1)
        pergunta_df_max_nivel = pergunta_df_max_nivel[['eixo', 'nivel', 'tema']].copy()
        
        if add_date:
            pergunta_df_max_nivel['data'] = self.empresa.data
            pergunta_df_max_nivel['data'] = pd.to_datetime(pergunta_df_max_nivel['data'], format='%d/%m/%Y')
        return pergunta_df_max_nivel

if __name__ == "__main__":
    import json
    with open("data.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    dataobj = Data.from_dict(data)
    niveis_aspectos = dataobj.get_aspecto_per_eixo()
    asdsa = dataobj.get_aspecto_per_eixo_and_tema()