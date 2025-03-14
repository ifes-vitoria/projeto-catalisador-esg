import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
from textwrap import wrap
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print('Instalar plotly: pip install plotly, para usar as funções de gráficos interativos e kaleido: pip install -U kaleido==0.1.0.post1, para graficos estáticos.')

WRAPSIZE_BARPLOT = 48
WRAPSIZE_SPIDER = 20
FIGSIZE = (10, 6)

class HTMLBlock:
    """A class to represent an HTML div block with optional CSS styling."""
    def __init__(self, content, styles=None):
        """
        Args:
            content (str): The HTML content inside the div.
            styles (dict): A dictionary of CSS styles to apply to the div.
        """
        self.content = content
        self.styles = styles or {}
    
    def render(self):
        """Render the HTML div block as a string."""
        style_str = '; '.join(f'{key}: {value}' for key, value in self.styles.items())
        return f'<div style="{style_str}">\n{self.content}\n</div>\n'

class HTMLDiv:
    def __init__(self, styles=None):
        self.styles = styles or {}
        self.contents = []
        
    def add_content(self, content) -> 'HTMLDiv':
        self.contents.append(content)
        return self
    
    def add_contents(self, contents) -> 'HTMLDiv':
        self.contents += contents
        return self
        
    def render(self):
        if len(self.contents) == 0:
            return ''
        style_str = '; '.join(f'{key}: {value}' for key, value in self.styles.items())
        content_str = '\n'.join(content for content in self.contents)
        if style_str != '':
            return f'<div style="{style_str}">\n{content_str}\n</div>\n'
        else:
            return f'<div>\n{content_str}\n</div>\n'

class HTMLTable:
    def __init__(self, styles=None):
        self.headers = []
        self.rows = []
        self.styles = styles or {}
    
    def add_headers(self, headers):
        self.headers += headers
    
    def add_rows(self, rows):
        self.rows += rows
        
    def render(self):
        def row_writer(row):
            return "\n".join(f"<td style='text-align: center; padding: 8px;'>{cell}</td>" for cell in row)
        
        header_str = ''.join(f'<th style="background-color: lightgray; padding: 8px;">{header}</th>' for header in self.headers)
        row_str = ''.join(f'<tr>{row_writer(row)}</tr>' for row in self.rows)
        style_str = '; '.join(f'{key}: {value}' for key, value in self.styles.items())
        if style_str!= '':
            style_str = f"{style_str}; border-collapse: collapse; margin: 0 auto; max-width: 80%; width: auto;"
        else:
            style_str = f"border-collapse: collapse; margin: 0 auto; max-width: 80%; width: auto;"
        style_str = f'"{style_str}"'
        return f'''
        <div style="text-align: center;">
            <table style={style_str}>
                <thead>
                    <tr>{header_str}</tr>
                </thead>
                <tbody>
                    {row_str}
                </tbody>
            </table>
        </div>
        '''

def wrap_txt(text, html_version=False, wrapsize=20):
    if html_version:
        return '<br>'.join(wrap(text, wrapsize))
    else:
        return '\n'.join(wrap(text, wrapsize))

def wrap_txt_list(texts, html_version=False, wrapsize=20):
    if html_version:
        return [wrap_txt(i, html_version=html_version, wrapsize=wrapsize) for i in texts]
    else:
        return [wrap_txt(i, html_version=html_version, wrapsize=wrapsize) for i in texts]

def create_header(title, level, center=False):
    """Create an HTML header string, optionally centered.

    Args:
        title (str): The text for the header.
        level (int): The level of the header (e.g., 1 for h1, 2 for h2).
        center (bool): Whether to center the header.

    Returns:
        str: An HTML header string.
    """
    header_html = f"<h{level}>{title}</h{level}>\n"
    if center:
        header_html = HTMLBlock(header_html, styles={'text-align': 'center'}).render()
    return header_html

def create_paragraph(text, center=False, bold=False):
    """Create an HTML paragraph string, optionally centered and bold.

    Args:
        text (str): The text for the paragraph.
        center (bool): Whether to center the paragraph.
        bold (bool): Whether to make the text bold.

    Returns:
        str: An HTML paragraph string.
    """
    if bold:
        text = f"<b>{text}</b>"
    paragraph_html = f"<p>{text}</p>\n"
    if center:
        paragraph_html = HTMLBlock(paragraph_html, styles={'text-align': 'center'}).render()
    return paragraph_html

def create_item_list(items, center=False):
    """Create an HTML unordered list string, optionally centered.

    Args:
        items (list of str): The items for the list.
        center (bool): Whether to center the list.

    Returns:
        str: An HTML unordered list string.
    """
    items_html = ''.join(f"<li>{item}</li>\n" for item in items)
    list_html = f"<ul>\n{items_html}</ul>\n"
    if center:
        list_html = HTMLBlock(list_html, styles={'text-align': 'center'}).render()
    return list_html

def create_spider_chart(categories, values, title, center=False, static=True):
    """Generate an HTML string containing a spider (radar) chart.

    Args:
        categories (list of str): The labels for each axis.
        values (list of float): The values corresponding to each category.

    Returns:
        str: An HTML div containing the spider chart.
    """
    # Ensure the loop is closed
    categories += categories[:1]
    values += values[:1]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself'
            )
        ],
        layout=go.Layout(
            title=title,
            polar=dict(
                radialaxis=dict(
                    visible=True
                )
            ),
            showlegend=False
        )
    )
    
    if static:
        img_bytes = fig.to_image(format='png', width=FIGSIZE[0]*100, height=FIGSIZE[1]*100, scale=1)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_html = f'<img src="data:image/png;base64,{img_base64}" alt="{title}">'
    else:
        img_html = fig.to_html(full_html=False)
    
    if center:
        img_html = HTMLBlock(img_html, styles={'text-align': 'center'}).render()
    
    return img_html

def create_spider_chart_matplot(categories, values, title, center=False):
    """Generate an HTML string containing a spider (radar) chart.

    Args:
        categories (list of str): The labels for each axis.
        values (list of float): The values corresponding to each category.

    Returns:
        str: An HTML img tag with the spider chart embedded as base64.
    """
    # Number of variables
    N = len(categories)

    # Repeat the first value to close the circular graph
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    # Set up the radar chart
    fig, ax = plt.subplots(figsize=FIGSIZE, subplot_kw=dict(polar=True))
    ax.set_title(title)
    
    # Draw the outline of the spider chart
    ax.plot(angles, values, 'o-', linewidth=2)
    ax.fill(angles, values, alpha=0.25)

    # Add the category labels
    ax.set_thetagrids(np.degrees(angles[:-1]), categories)

    # Set the range of radial axis
    ax.set_rlabel_position(30)
    ax.grid(True)

    # Save the figure to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    img_data = buffer.getvalue()
    encoded = base64.b64encode(img_data).decode('utf-8')
   
    img_html = f'<img src="data:image/png;base64,{encoded}" />\n'
    
    if center:
        img_html = HTMLBlock(img_html, styles={'text-align': 'center'}).render()
    
    return img_html

def create_timeseries_chart(dates, values, legends, title, xlabel, ylabel, center=False, static=True):
    """Generate an HTML string containing a time series chart.

    Args:
        dates (list of datetime): The dates for the x-axis.
        values (list of float): The values for the y-axis.

    Returns:
        str: An HTML div containing the time series chart.
    """
    fig = go.Figure([
        go.Scatter(x=date_series, y=value_series, name=legend) \
            for date_series, value_series, legend in zip(dates, values, legends)
    ])
    fig.update_xaxes(title_text=xlabel, tickformat='%d/%m/%Y', tickangle=-45)
    fig.update_yaxes(title_text=ylabel)
    fig.update_layout(title=title)
    
    if static:
        img_bytes = fig.to_image(format='png', width=FIGSIZE[0]*100, height=FIGSIZE[1]*100, scale=1)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_html = f'<img src="data:image/png;base64,{img_base64}" alt="{title}">'
    else:
        img_html = fig.to_html(full_html=False)
    
    if center:
        img_html = HTMLBlock(img_html, styles={'text-align': 'center'}).render()
    
    return img_html

def create_timeseries_chart_matplot(dates, values, legends, title, xlabel, ylabel, center=False):
    """Generate an HTML string containing a time series chart.

    Args:
        dates (list of datetime): The dates for the x-axis.
        values (list of float): The values for the y-axis.

    Returns:
        str: An HTML img tag with the time series chart embedded as base64.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for date_series, value_series, legend in zip(dates, values, legends):
        ax.plot(date_series, value_series, linestyle='-', marker='o', label=legend)
    ax.legend()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)

    # Format x-axis labels
    fig.autofmt_xdate()

    # Save the figure to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    img_data = buffer.getvalue()
    encoded = base64.b64encode(img_data).decode('utf-8')

    img_html = f'<img src="data:image/png;base64,{encoded}" />\n'

    if center:
        img_html = HTMLBlock(img_html, styles={'text-align': 'center'}).render()
    
    return img_html

def create_bar_plot_matplot(categories, values, title, xlabel, ylabel, center=False, horizontal=False):
    """Generate an HTML string containing a bar plot chart.

    Args:
        categories (list of str): The categories for the x-axis.
        values (list of float): The values for the y-axis.

    Returns:
        str: An HTML img tag with the bar plot embedded as base64.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)
    bar_width = 0.8
    margin_add = 0.05
    if horizontal:
        ax.barh(categories, values, color='skyblue', height=bar_width)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_yticks(np.arange(len(categories)))
        ax.set_yticklabels(categories, wrap=True)
        ax.tick_params(axis='y', pad=12)
    else:
        ax.bar(categories, values, color='skyblue', width=bar_width)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xticks(np.arange(len(categories)))
        ax.set_xticklabels(categories, wrap=True)
    
    if horizontal:
        ax.margins(x=margin_add)
    else:
        ax.margins(y=margin_add)
    
    ax.set_title(title)
    ax.grid(True)

    # Save the figure to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    img_data = buffer.getvalue()
    encoded = base64.b64encode(img_data).decode('utf-8')

    img_html = f'<img src="data:image/png;base64,{encoded}" />\n'
    if center:
        img_html = HTMLBlock(img_html, styles={'text-align': 'center'}).render()
    
    return img_html

def create_bar_plot(categories, values, title, xlabel, ylabel, center=False, horizontal=False, static=True):
    """Generate an HTML string containing a bar plot chart.

    Args:
        categories (list of str): The categories for the x-axis.
        values (list of float): The values for the y-axis.

    Returns:
        str: An HTML div containing the bar plot.
    """
    if horizontal:
        fig = go.Figure([go.Bar(y=categories, x=values, orientation='h')])
    else:
        fig = go.Figure([go.Bar(x=categories, y=values)])
    fig.update_layout(title=title)
    fig.update_xaxes(title_text=xlabel)
    fig.update_yaxes(title_text=ylabel)
    
    if static:
        img_bytes = fig.to_image(format='png', width=FIGSIZE[0]*100, height=FIGSIZE[1]*100, scale=1)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_html = f'<img src="data:image/png;base64,{img_base64}" alt="{title}">'
    else:
        img_html = fig.to_html(full_html=False)
    
    if center:
        img_html = HTMLBlock(img_html, styles={'text-align': 'center'}).render()
    
    return img_html

def timeseries_chart(dates, values, legends, title, xlabel, ylabel, center=False, matplot=False, static=True):
    as_matplot = matplot or not HAS_PLOTLY
    title_now = wrap_txt(title, html_version=not as_matplot, wrapsize=WRAPSIZE_SPIDER)
    legends_now = wrap_txt_list(legends, html_version=not as_matplot, wrapsize=WRAPSIZE_SPIDER)
    if as_matplot:
        return create_timeseries_chart_matplot(dates, values, legends_now, title_now, xlabel, ylabel, center)
    else:
        return create_timeseries_chart(dates, values, legends_now, title_now, xlabel, ylabel, center, static=static)

def spider_chart(categories, values, title, center=False, matplot=False, static=True):
    as_matplot = matplot or not HAS_PLOTLY
    categories_now = wrap_txt_list(categories, html_version=not as_matplot, wrapsize=WRAPSIZE_SPIDER)
    title_now = wrap_txt(title, html_version=not as_matplot, wrapsize=WRAPSIZE_SPIDER)
    if as_matplot:
        return create_spider_chart_matplot(categories_now, values, title_now, center)
    else:
        return create_spider_chart(categories_now, values, title_now, center, static=static)

def bar_plot(categories, values, title, xlabel, ylabel, center=False, matplot=False, horizontal=False, static=True):
    as_matplot = matplot or not HAS_PLOTLY
    categories_now = wrap_txt_list(categories, html_version=not as_matplot, wrapsize=WRAPSIZE_BARPLOT)
    title_now = wrap_txt(title, html_version=not as_matplot, wrapsize=WRAPSIZE_BARPLOT)
    if as_matplot:
        return create_bar_plot_matplot(categories_now, values, title_now, xlabel, ylabel, center, horizontal)
    else:
        return create_bar_plot(categories_now, values, title_now, xlabel, ylabel, center, horizontal, static=static)

def embed_local_image(image_path, center=False):
    """Embed a local image into an HTML string.

    Args:
        image_path (str): The file path to the local image.

    Returns:
        str: An HTML img tag with the image embedded as base64.
    """
    with open(image_path, 'rb') as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
    extension = image_path.split('.')[-1]
    img_html = f'<img src="data:image/{extension};base64,{encoded_string}" />\n'
    if center:
        img_html = HTMLBlock(img_html, styles={'text-align': 'center'}).render()
    
    return img_html

if __name__ == '__main__':
    import pandas as pd
    html_content = ''
    # Add a header
    html_content += create_header("My Report", 1, center=True)

    # Add a spider chart
    categories = ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency', 'Something very long that should fit into multiple lines']
    values = [90, 80, 85, 70, 95, 100]
    html_content += create_header("Spider Chart Example", 2, center=True)
    html_content += spider_chart(categories, values, '', center=True, matplot=True)
    
    # Add a time series chart
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    values = np.random.randn(100).cumsum()
    html_content += create_header("Time Series Chart Example", 2, center=True)
    html_content += timeseries_chart(dates, values, '', 'Data', 'Valores', center=True, matplot=True)

    # Add a bar plot
    categories = ['Category A', 'Category B', 'Category C', 'Category with a very long name']
    values = [20, 35, 30, 40]
    html_content += create_header("Bar Plot Example", 2, center=True)
    html_content += bar_plot(categories, values, '', 'Data', 'Valores', center=True, matplot=True)

    # Embed a local image
    html_content += create_header("Embedded Image Example", 2, center=True)
    # html_content += embed_local_image('path_to_your_image.jpg')

    # Save the HTML content to a file
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
