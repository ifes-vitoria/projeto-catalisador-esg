from report.main import (
    conteudo_header,
    conteudo_resumo_maturidade,
    conteudo_recomendacoes,
    conteudo_maturidade_final,
    conteudo_spiders,
    conteudo_indicadores,
    combine_multiple_reports,
    conteudo_indicadores_no_tempo,
    conteudo_producao_no_tempo,
    write_html
)
from report.models import Data
from typing import List

def report_generation(datas: List[Data]):

    # ultimo relatório
    dataobj = datas[-1]
    # dataobj = Data.from_dict(data)
    niveis_aspectos = dataobj.get_aspecto_per_eixo()
    niveis_aspectos_tema_dataframe = dataobj.get_aspecto_per_eixo_and_tema()
    
    # conteudo de ultimo relatório    
    comeco = conteudo_header(dataobj)
    resumo_maturidade = conteudo_resumo_maturidade(dataobj, niveis_aspectos)
    resumo_recomendacoes = conteudo_recomendacoes(dataobj, niveis_aspectos)
    resumo_maturidade_final = conteudo_maturidade_final(dataobj, niveis_aspectos)
    resumo_spiders = conteudo_spiders(dataobj, niveis_aspectos, niveis_aspectos_tema_dataframe, matplot=False)
    resumo_indicadores = conteudo_indicadores(dataobj, horizontal=True, matplot=False, split_indicadores_charts=True)
    
    # pegar series temporais
    # dataobjs = [Data.from_dict(i) for i in datas]
    dataobjs = datas
    niveis_aspectos, niveis_aspectos_tema, indicadores_df, producao_df = combine_multiple_reports(dataobjs)
    maturidade_html, tema_indicadores_html, indicadores_html = conteudo_indicadores_no_tempo(
        niveis_aspectos, niveis_aspectos_tema, indicadores_df, matplot=False,
        split_maturidade_charts=True, split_indicadores_charts=True
    )

    producao_html = conteudo_producao_no_tempo(
        producao_df, dataobj.empresa.unidproducao, matplot=False
    )

    html_content = ''
    html_content += comeco.render()
    html_content += resumo_maturidade.render()
    html_content += resumo_recomendacoes.render()
    html_content += producao_html.render()
    html_content += resumo_indicadores.render()
    html_content += resumo_maturidade_final.render()
    html_content += resumo_spiders.render()
    html_content += tema_indicadores_html.render()
    html_content += maturidade_html.render()
    html_content += indicadores_html.render()
    return write_html({'nome_empresa': dataobj.empresa.nome_empresa, "data": dataobj.empresa.data}, html_content)

if __name__ == "__main__":
    
    import json
    from datetime import datetime
    import pandas as pd
    import copy
    def load_data(datapathh):
        datapathh
        with open("data.json", "r", encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def create_mock_timeseries(data, length=10):
        datas = []
        for k in pd.date_range(start=datetime.strptime(data["data"], "%d/%m/%Y"), periods=length).strftime("%d/%m/%Y").tolist():
            data['data'] = k
            datas.append(copy.copy(data))
        return datas
    
    # Input para o relatório
    datas = create_mock_timeseries(load_data("data.json"), length=56)
    report_generation(datas)