import plotly.graph_objs as go
from plotly.subplots import make_subplots
from settings import colors


def tabela_recomendada(titulo:str, carteira:list)->go.Figure:
    font_dict = {'family': "Segoe UI", 'size': 16, 'color': "black"}
    tags={}
    for ativo in carteira:
        tags[ativo.tag]=tags[ativo.tag]+ativo.weight if ativo.tag in tags.keys() else ativo.weight

    # Sample data for the pie chart
    pie_labels = list(tags.keys())
    pie_values = [tags[i]*100 for i in tags.keys()]

    # Sample data for the tables
    table_data = [
        [
            [i.ticker for i in carteira if i.tag == classe and i.weight>0],
            [format(round(i.weight*100,2),'.2f') for i in carteira if i.tag == classe and i.weight>0] 
        ] for classe in tags.keys()
    ]
        
    # Create a subplot grid (1 row, 5 columns)
    fig = make_subplots(rows=4, cols=2, column_widths=[0.3, 0.70],
                        specs=[[{'type': 'pie', 'rowspan':3}, {'type': 'table'}],
                               [None, {'type': 'table'}],
                               [None, {'type': 'table'}],
                               [None, {'type': 'table'}]])

    # Add the pie chart
    fig.add_trace(go.Pie(labels=pie_labels, 
                         values=pie_values, 
                         textinfo='label+percent', 
                         hoverinfo='none',
                         marker_colors=colors[1:], 
                         textfont=font_dict), row=1, col=1)

    # Add tables for each slice
    for i, (details, weights) in enumerate(table_data):
        #row = 1 if i < 2 else 2  # First two tables in the first row, next two in the second row
        #col = 3 if i % 2 == 0 else 2  # Alternate columns for the tables
        row=i+1
        col=2
        if sum([float(i) for i in weights])>0:
            fig.add_trace(go.Table(
                header=dict(values=[f'{pie_labels[i]}', 'Peso'], align="left", font=font_dict),
                cells=dict(values=[details, weights], align="left", height=30, font=font_dict),
                columnwidth=[70,30]
            ), row=row, col=col)

    # Update layout
    fig.update_layout(title_text="",
                      title_font=dict(family="Bodoni MT", size=20, color="black"),
                      showlegend=False,
                      legend=dict(
                        orientation='v',
                        x=0,
                        y=0.5,
                        xanchor='left',
                        yanchor='top'),
                        width=2000, height=820)

    return fig


if __name__=="__main__":
    from carteiras import recomendadas
    import os
    
    for perf in ["Mercúrio","Vênus","Terra","Marte","Júpiter"]:
        idx=max(recomendadas[perf].keys())
        carteira=recomendadas[perf][idx]
        fig=tabela_recomendada(perf,carteira)
        fig.show()
        fig.write_image(os.path.join(".","calc_perfis","figures",perf+"_recomendada.png"))