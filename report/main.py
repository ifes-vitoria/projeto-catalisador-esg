import numpy as np
import pandas as pd
from typing import List
import report.models as models
from report.generate_html import (
    HTMLDiv, HTMLTable,
    create_header, create_paragraph, create_item_list,
    spider_chart, bar_plot, timeseries_chart
)

def conteudo_header(dataobj: models.Data):
    comeco = HTMLDiv().add_contents([
        create_header(f"Relatório ESG - {dataobj.empresa.nome_empresa}", 1),
        create_paragraph(f"Data: {dataobj.empresa.data}"),
        create_paragraph(f"Localização: {dataobj.empresa.localizacao}")
    ])
    return comeco

def conteudo_resumo_maturidade(dataobj: models.Data, niveis_aspectos: List[models.EixoMaturidade]):
    table = HTMLTable()
    table.add_headers(['Aspecto','Nível de Maturidade','Descrição'])
    table.add_rows([[nivel_aspecto.eixo.capitalize(), nivel_aspecto.nivel, nivel_aspecto.maturidade.descricao] for nivel_aspecto in niveis_aspectos])
    
    resumo_maturidade_obj = HTMLDiv().add_contents([
        create_header(f"Resumo de Maturidade ESG", 2),
        table.render()
    ])
    return resumo_maturidade_obj

def conteudo_recomendacoes(dataobj: models.Data, niveis_aspectos: List[models.EixoMaturidade]):
    recomendacoes_list = []
    for nivel_aspecto in niveis_aspectos:
        recomendacoes_list += [
            create_paragraph(nivel_aspecto.eixo.capitalize()+':', bold=True),
            create_item_list(nivel_aspecto.recomendacoes.recomendacoes)
        ]
    resumo_recomendacoes = HTMLDiv().add_contents(
        [create_header(f"Resumo de Recomendações", 2)] + recomendacoes_list
    )
    return resumo_recomendacoes

def conteudo_maturidade_final(dataobj: models.Data, niveis_aspectos: List[models.EixoMaturidade], usar_todos=True):
    aspecto_final = niveis_aspectos[np.argmin([i.nivel for i in niveis_aspectos])] # menor nivel
    aspecto_final_maturidade = aspecto_final.maturidade
    if usar_todos:
        recomendacoes_list = create_item_list(models.RecommendationLevel.get_all_lvl_description(aspecto_final.nivel))
    else:
        recomendacoes_list = create_item_list(aspecto_final.recomendacoes.recomendacoes)
        
    resumo_maturidade_final = HTMLDiv().add_contents([
        create_header(f"Maturidade Final", 2),
        create_paragraph(f"Nível de Maturidade: {aspecto_final_maturidade.nivel}. Estágio: {aspecto_final_maturidade.titulo}"),
        create_paragraph(f"Descrição", bold=True),
        create_paragraph(aspecto_final_maturidade.descricao),
        create_paragraph(f"Recomendações", bold=True),
        recomendacoes_list
    ])
    return resumo_maturidade_final

def conteudo_spiders(dataobj: models.Data, niveis_aspectos: List[models.EixoMaturidade], niveis_aspectos_tema_dataframe: pd.DataFrame, matplot: bool =True):
    resumo_spiders = HTMLDiv()
    
    for nivel_aspecto in niveis_aspectos:
        eixo = nivel_aspecto.eixo
        dataframe_eixo = niveis_aspectos_tema_dataframe[niveis_aspectos_tema_dataframe.eixo==nivel_aspecto.eixo][['tema', 'nivel']]
        header_str = create_header(f"Resultado de Maturidade dos Temas do Aspecto {eixo.capitalize()}", 2, center=True)
        spider_str = spider_chart(categories=dataframe_eixo.tema.tolist(), values=dataframe_eixo.nivel.tolist(), title='', center=True, matplot=matplot)
        resumo_spiders.add_contents([header_str, spider_str])
    return resumo_spiders

def conteudo_indicadores(dataobj: models.Data, matplot: bool = True, horizontal: bool = False, split_indicadores_charts: bool = False):
    indicadores_df = pd.DataFrame([i.model_dump() for i in dataobj.indicadores])
    html_contents = []
    for eixo in indicadores_df['eixo'].unique():
        eixo_df = indicadores_df[indicadores_df['eixo']==eixo]
        eixo_df.item.tolist()
        eixo_df.valor.tolist()
        html_contents += [create_header(f"Indicadores {eixo.capitalize()}", 2)]
        if split_indicadores_charts:
            html_contents += [
                bar_plot([eixo_df_item], [eixo_df_valor], title='', xlabel='Resultado', ylabel='', center=True, matplot=matplot, horizontal=horizontal) \
                for eixo_df_item, eixo_df_valor in zip(eixo_df.item.tolist(), eixo_df.valor.tolist(),)
            ]
        else:
            html_contents += [bar_plot(eixo_df.item.tolist(), eixo_df.valor.tolist(), title='', xlabel='Resultado', ylabel='', center=True, matplot=matplot, horizontal=horizontal)]
    return HTMLDiv().add_contents(html_contents)

def conteudo_producao_no_tempo(producao: pd.DataFrame, unidproducao: str, matplot: bool = True) -> HTMLDiv:
    dates = producao.date.tolist()
    values = producao.producao.tolist()

    try:
        maturidade_html = HTMLDiv().add_contents([
            create_header(f"Produção", 2, center=True),
            timeseries_chart([dates], [values], legends=[f'Produção {unidproducao}'], title="", xlabel='Data', ylabel=f'Produção {unidproducao}', center=True, matplot=matplot),
        ])
    except:
        maturidade_html = HTMLDiv()
    return maturidade_html
   
def conteudo_indicadores_no_tempo(niveis_aspectos: pd.DataFrame, niveis_aspectos_tema: pd.DataFrame, indicadores_df: pd.DataFrame, matplot: bool = True, split_maturidade_charts: bool = False, split_indicadores_charts: bool = False):
    eixos = niveis_aspectos.eixo.unique().tolist()
    dates = []
    values = []
    
    maturidade_temas = []
    tema_indicadores = []
    for eixo in eixos:
        eixo_df = niveis_aspectos[niveis_aspectos['eixo']==eixo]
        eixo_tema_df = niveis_aspectos_tema[niveis_aspectos_tema['eixo']==eixo]
        indicadores_tema_df = indicadores_df[indicadores_df['eixo']==eixo]
        values.append(eixo_df.nivel.tolist())
        dates.append(eixo_df.data.tolist())
        
        temas = eixo_tema_df.tema.unique()
        indicadores = indicadores_tema_df.item.unique()
        indicador_dates = []
        indicador_values = []
        tema_dates = []
        tema_values = []
        
        maturidade_temas.append(create_header(f"Temas de Maturidade {eixo.capitalize()} no tempo", 2, center=True))
        for tema in temas:
            temas_no_eixo_df = eixo_tema_df[eixo_tema_df.tema==tema]
            tema_values.append(temas_no_eixo_df.nivel.tolist())
            tema_dates.append(temas_no_eixo_df.data.tolist())
            if split_maturidade_charts:
                maturidade_temas.append(create_header(tema.capitalize() + 'no tempo', 3, center=True))
                timeseries_html = timeseries_chart(tema_dates, tema_values, legends=[tema.capitalize()], title="", xlabel='Data', ylabel='Valor', center=True, matplot=matplot)
                maturidade_temas.append(timeseries_html)
        
        tema_indicadores.append(create_header(f"Indicadores {eixo.capitalize()} no tempo", 2, center=True))
        for indicador in indicadores:
            indicadores_tema_no_eixo_df = indicadores_tema_df[indicadores_tema_df.item==indicador]
            indicador_values.append(indicadores_tema_no_eixo_df.valor.tolist())
            indicador_dates.append(indicadores_tema_no_eixo_df.data.tolist())
            if split_indicadores_charts:
                tema_indicadores.append(create_header(indicador.capitalize() + 'no tempo', 3, center=True))
                indicadores_timeseries_html = timeseries_chart(indicador_dates, indicador_values, legends=[indicador.capitalize()], title="", xlabel='Data', ylabel='Valor', center=True, matplot=matplot)
                tema_indicadores.append(indicadores_timeseries_html)
        
        if not split_maturidade_charts:
            maturidade_temas.append(timeseries_chart(
                tema_dates, tema_values, legends=[tema.capitalize() for tema in temas], title="", xlabel='Data', ylabel='Valor', center=True, matplot=matplot
            ))
        
        if not split_indicadores_charts:
            tema_indicadores.append(timeseries_chart(
                indicador_dates, indicador_values, legends=[indicador.capitalize() for indicador in indicadores], title="", xlabel='Data', ylabel='Valor', center=True, matplot=matplot
            ))

    maturidade_temas_html = HTMLDiv().add_contents(maturidade_temas)
    indicadores_html = HTMLDiv().add_contents(tema_indicadores)
    maturidade_html = HTMLDiv().add_contents([
        create_header(f"Maturidade no tempo", 2, center=True),
        timeseries_chart(dates, values, legends=[i.capitalize() for i in eixos], title="", xlabel='Data', ylabel='Valor', center=True, matplot=matplot),
    ])
    return maturidade_html, maturidade_temas_html, indicadores_html
   
def write_html(data, conteudo, arquivo='report.html') -> str:
    string_html = f'''
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório ESG {data["nome_empresa"]} - {data["data"]}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                table, th, td {{ border: 1px solid #ddd; }}
                th, td {{ padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .recommendations {{ margin-bottom: 40px; }}
                .recommendations ul {{ margin-top: 0; }}
            </style>
        </head>
    <body>
    {conteudo}
    </body>
    </html>
    '''
    # # Save the HTML content to a file
    # with open(arquivo, 'w', encoding='utf-8') as f:
    #     f.write(string_html)
    return string_html

def combine_multiple_reports(dataobjs: List[models.Data]):
    indicadores_df = []
    for dataobj in dataobjs:
        indicador_df = pd.DataFrame([i.model_dump() for i in dataobj.indicadores])
        indicador_df['data'] = dataobj.empresa.data
        indicadores_df.append(indicador_df)
    indicadores_df = pd.concat(indicadores_df)
    indicadores_df['data'] = pd.to_datetime(indicadores_df['data'], format='%d/%m/%Y')
    
    niveis_aspectos = pd.concat([pd.DataFrame(
        [{'eixo': k.eixo, 'nivel': k.nivel, 'data': k.data} for k in report_i.get_aspecto_per_eixo(add_date=True)]
    ) for report_i in dataobjs])
    niveis_aspectos['data'] = pd.to_datetime(niveis_aspectos['data'], format='%d/%m/%Y')
    niveis_aspectos_tema = pd.concat([report_i.get_aspecto_per_eixo_and_tema(add_date=True) for report_i in dataobjs])

    producao_df = pd.DataFrame([{'producao': i.empresa.producaomes, 'date': i.empresa.data} for i in dataobjs])
    producao_df['producao'] = pd.to_numeric(producao_df['producao'], errors='coerce')
    producao_df['date'] = pd.to_datetime(producao_df['date'], format='%d/%m/%Y')
    return niveis_aspectos, niveis_aspectos_tema, indicadores_df, producao_df

if __name__ == "__main__":
    
    import json
    from datetime import datetime
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
    

    # ultimo relatório
    data = datas[-1]
    dataobj = models.Data.from_dict(data)
    niveis_aspectos = dataobj.get_aspecto_per_eixo()
    niveis_aspectos_tema_dataframe = dataobj.get_aspecto_per_eixo_and_tema()
    
    # conteudo de ultimo relatório    
    comeco = conteudo_header(dataobj)
    resumo_maturidade = conteudo_resumo_maturidade(dataobj, niveis_aspectos)
    resumo_recomendacoes = conteudo_recomendacoes(dataobj, niveis_aspectos)
    resumo_maturidade_final = conteudo_maturidade_final(dataobj, niveis_aspectos)
    resumo_spiders = conteudo_spiders(dataobj, niveis_aspectos, niveis_aspectos_tema_dataframe, matplot=False)
    resumo_indicadores = conteudo_indicadores(dataobj, horizontal=True, matplot=False, split_indicadores_charts=False)
    
    # pegar series temporais
    dataobjs = [models.Data.from_dict(i) for i in datas]
    niveis_aspectos, niveis_aspectos_tema, indicadores_df = combine_multiple_reports(dataobjs)
    maturidade_html, tema_indicadores_html, indicadores_html = conteudo_indicadores_no_tempo(
        niveis_aspectos, niveis_aspectos_tema, indicadores_df, matplot=False,
        split_maturidade_charts=True, split_indicadores_charts=True
    )
    
    html_content = ''
    html_content += comeco.render()
    html_content += resumo_maturidade.render()
    html_content += resumo_recomendacoes.render()
    html_content += resumo_indicadores.render()
    html_content += resumo_maturidade_final.render()
    html_content += resumo_spiders.render()
    html_content += tema_indicadores_html.render()
    html_content += maturidade_html.render()
    html_content += indicadores_html.render()
    htmlstring = write_html(data, html_content)
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(htmlstring)