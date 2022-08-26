from __future__ import annotations
import plotly.express as px
import plotly.graph_objects as go
from app import db
import dash_bootstrap_components as dbc
from dash import html
from flask import session

from models import DeathStat


profession_colours = {
    'Guardian': '#186885',
    'Dragonhunter': '#186885',
    'Firebrand': '#186885',
    'Willbender': '#186885',
    'Revenant': '#661100',
    'Herald': '#661100',
    'Renegade': '#661100',
    'Vindicator': '#661100',
    'Warrior': '#CAAA2A',
    'Berserker': '#CAAA2A',
    'Spellbreaker': '#CAAA2A',
    'Bladesworn': '#CAAA2A',
    'Engineer': '#87581D',
    'Scrapper': '#87581D',
    'Holosmith': '#87581D',
    'Mechanist': '#87581D',
    'Ranger': '#67A833',
    'Druid': '#67A833',
    'Soulbeast': '#67A833',
    'Untamed': '#67A833',
    'Thief': '#974550',
    'Daredevil': '#974550',
    'Deadeye': '#974550',
    'Specter': '#974550',
    'Elementalist': '#DC423E',
    'Tempest': '#DC423E',
    'Weaver': '#DC423E',
    'Catalyst': '#DC423E',
    'Mesmer': '#69278A',
    'Chronomancer': '#69278A',
    'Mirage': '#69278A',
    'Virtuoso': '#69278A',
    'Necromancer': '#2C9D5D',
    'Reaper': '#2C9D5D',
    'Scourge': '#2C9D5D',
    'Harbinger': '#2C9D5D',
}

profession_shorts = {
    'Guardian': 'Gdn',
    'Dragonhunter': 'Dgh',
    'Firebrand': 'Fbd',
    'Willbender': 'Wbr',
    'Revenant': 'Rev',
    'Herald': 'Her',
    'Renegade': 'Ren',
    'Vindicator': 'Vin',
    'Warrior': 'War',
    'Berserker': 'Brs',
    'Spellbreaker': 'Spb',
    'Bladesworn': 'Bls',
    'Engineer': 'Eng',
    'Scrapper': 'Scr',
    'Holosmith': 'Hls',
    'Mechanist': 'Mec',
    'Ranger': 'Rgr',
    'Druid': 'Dru',
    'Soulbeast': 'Slb',
    'Untamed': 'Unt',
    'Thief': 'Thf',
    'Daredevil': 'Dar',
    'Deadeye': 'Ded',
    'Specter': 'Spe',
    'Elementalist': 'Ele',
    'Tempest': 'Tmp',
    'Weaver': 'Wea',
    'Catalyst': 'Cat',
    'Mesmer': 'Mes',
    'Chronomancer': 'Chr',
    'Mirage': 'Mir',
    'Virtuoso': 'Vir',
    'Necromancer': 'Nec',
    'Reaper': 'Rea',
    'Scourge': 'Scg',
    'Harbinger': 'Hrb',
}

raid_types = {
    'morning',
    'afternoon',
    'guild',
    'unknown',
    'reset'
}

general_layout = {
        'title_xanchor':'center',
        'title_x':0.5,
        'legend_y':0,
        'legend_x':0.9,
        'margin':dict(l=200, t=20, b=20),
        'font_size':13,
        'yaxis_title':'',
        'paper_bgcolor':'rgba(0,0,0,0)',
        'plot_bgcolor':'rgba(0,0,0,0)',
        'font_color':'#EEE',
        'yaxis_automargin': False,
        'yaxis_ticksuffix': ' ',
        'yaxis_tickfont_size': 15,
        'yaxis_showticklabels': False,
        'xaxis_rangemode': 'tozero',
        'xaxis_gridcolor':'grey',
}

general_layout_line = {
        'title_xanchor':'center',
        'title_x':0.5,
        'legend_y':1,
        'legend_x':1,
        'font_size':13,
        'paper_bgcolor':'rgba(0,0,0,0)',
        'plot_bgcolor':'rgba(0,0,0,0)',
        'font_color':'#EEE',
        'xaxis_showline': True
}

def get_top_bar_chart(df, t, title, legend = True, detailed = False):
    fig = px.bar(df, y="Name", x="Total", 
                 color="Profession", 
                 text="Total",
                 text_auto=',',
                 barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours
                 )
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        xaxis_title="Times top / Times attended - Total | avg per sec",
        # title=title,
        showlegend=legend
    )
    fig.update_layout(general_layout)
    fig.update_traces(textangle=0, width=0.8)
    fig = add_annotations_graph(fig, df, t)
    if detailed:
        fig = add_sorting_options(fig, df, t)
    return fig


def add_annotations_graph(fig, df, t):
    for name in df["Name"]:
        if not isinstance(t(), DeathStat):
            avg_s = df[df["Name"] == name]["Average per s"].values[0]
            fig.add_annotation(y=name, x=int(df[df["Name"] == name]["Total"].values[0]),
                               text="{:,.0f}".format(avg_s) if avg_s >= 10 else "{:,.2f}".format(avg_s),
                               showarrow=False,
                               yshift=0,
                               xshift=2,
                               xanchor="left",
                               font_size=13,
            ),
        text = f"""<a href="/details/{name}" target='_self'>{name}</a>"""
        color='#EEE'
        background_color=None
        #border = '#303030'
        if name[0].isdigit():
            text = name
            color = 'grey'
        if 'CHARACTERS' in session:
            #print(f"{name.rsplit(' ', 1)[0]=}")
            if name.rsplit(' ', 1)[0] in session['CHARACTERS']:
                #print(f"FOUND ON: {name.rsplit(' ', 1)[0]}")
                background_color='#616161'
                #border = '#414141'
        fig.add_annotation(y=name, x=0,
                            text=text,
                            showarrow=False,
                            yshift=0,
                            xshift=-2,
                            xanchor="right",
                            font_size=13,
                            font_color=color,
                            bgcolor=background_color,
                            #bordercolor=border
        ),
        fig.add_annotation(y=name, x=0,
                text=" " + str(int(df[df["Name"] == name]["Times Top"].values[0]))
                    + " / " +
                    str(int(df[df["Name"] == name]["Attendance (number of fights)"].values[0])),
                showarrow=False,
                yshift=0,
                xshift=0,
                xanchor="left",
                font_size=13,
        )
    return fig


def add_clickable_names(fig, df):
    for name in df["Name"]:
        text = f"""<a href="/details/{name}" target='_self'>{name}</a>"""
        color='#EEE'
        if name[0].isdigit():
            text = name
            color = 'grey'
        fig.add_annotation(y=name, x=0,
                            text=text,
                            showarrow=False,
                            yshift=0,
                            xshift=2,
                            xanchor="right",
                            font_size=13,
                            font_color=color
        )
    return fig


def get_top_dist_bar_chart(df, t, legend=True):
    #only range from 0-100 in detailed
    xaxis_range = None
    if len(df) > 5:
        xaxis_range = [0,100]
    fig = px.bar(df, y="Name", x="Percentage Top", color="Profession", barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours)
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        xaxis_ticksuffix="%",
        xaxis_title="% times top closest to tag",
        xaxis_range=xaxis_range,
        # title=t,
    )
    fig.update_layout(general_layout)
    fig = add_times_top_annotation(fig, df)
    fig = add_clickable_names(fig, df)

    for name in df["Name"]:
        fig.add_annotation(y=name, x=df[df["Name"] == name]["Percentage Top"].values[0],
                           text="{}%".format(df[df["Name"] ==  name]["Percentage Top"].values[0]),
                           showarrow=False,
                           yshift=0,
                           xshift=0,
                           xanchor="right",
                           font_size=13,
                           )
    return fig


def add_times_top_annotation(fig, df):
    for name in df["Name"]:
        fig.add_annotation(y=name, x=0,
                    text=" " + str(int(df[df["Name"] == name]["Times Top"].values[0]))
                        + " / " +
                        str(int(df[df["Name"] == name]["Attendance (number of fights)"].values[0])),
                    showarrow=False,
                    yshift=0,
                    xshift=0,
                    xanchor="left",
                    font_size=13,
        )
    return fig
    

def get_pie_chart(df, title, colors):
    fig = px.pie(df, values="values", names="names",color_discrete_sequence=colors)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#EEE',
        title=title,
        title_x=0.5,
        height=500,
    )
    fig.update_traces(
        marker=dict(colors=colors, line=dict(color='#7C8789', width=2)),
        textposition='inside',
        textinfo='percent+label'
    )
    return fig


def get_summary_table(df):
    try:
        if df is not None:
            table = dbc.Table.from_dataframe(df.drop('Title', axis=1), striped=True, bordered=True, hover=True, size='sm', id='summary')
            return [table, html.Hr()]
        return None
    except Exception as e:
        db.session.rollback()
        print(e)
        return None

#Total dmg_taken
def get_top_dmg_taken_chart(df, t, title, legend = True):
    fig = px.bar(df, y=df["Name"], x=df["Average per s"], 
                 color=df["Name"],
                 hover_name="Name",
                 text=df['Profession'],
                 text_auto=',',
                 barmode="relative",
                 orientation='h',
                 color_discrete_sequence=df["Profession_color"].values
                 )
    fig.update_layout(
        xaxis_title="Times top / Times attended - (Deaths) - per sec | Total ",
        title=title,
        showlegend=legend,
        legend_y=1,
        legend_x=0.9,
    )
    fig.update_layout(general_layout)
    fig.update_traces(textangle=0)
    fig = add_times_top_annotation(fig, df)
    fig = add_clickable_names(fig, df)

    for name in df['Name']:
        fig.add_annotation(y=name, x=int(df[df["Name"] == name]["Average per s"].values[0]),
                                text="{:,.0f}".format(df[df["Name"] == name]["Total"].values[0]),
                                showarrow=False,
                                yshift=0,
                                xshift=2,
                                xanchor="left",
                                font_size=13,
        )
    for name in df['Name']:
        fig.add_annotation(y=name, x=int(df.iloc[0]["Average per s"]/2),
                                text="{:,.0f}".format(df[df["Name"] == name]["Total Deaths"].values[0]),
                                showarrow=False,
                                yshift=0,
                                xshift=2,
                                xanchor="left",
                                font_size=13,
        )
    fig.update_layout(
        updatemenus=[
            dict(
                x=-0.1,
                y=1.06,
                active=0,
                bordercolor='#888',
                borderwidth=2,
                bgcolor='#303030',
                showactive=False,
                buttons=[
                    dict(label="Average",
                            method="relayout",
                            args=["yaxis", {"categoryarray": (df.sort_values(by="Average per s", ascending=False))["Name"],
                                            "categoryorder": "array",
                                            'showticklabels': False}]),
                    dict(label="Deaths",
                            method="relayout",
                            args=["yaxis", {"categoryarray": (df.sort_values(by=["Total Deaths","Average per s"], ascending=[True, False]))["Name"],
                                            "categoryorder": "array",
                                            'showticklabels': False}]),
                ]
            )
        ]
    )
    return fig


def get_top_survivor_chart(df, t, title, legend = False):
    fig = px.bar(df, y=df["Name"], x=df["Total deaths"], 
                color=df["Name"],
                hover_name="Name",
                text=df['Profession'],
                text_auto=',',
                barmode="relative",
                orientation='h',
                color_discrete_sequence=df["Profession_color"]
                )
    fig.update_layout(
                xaxis_title="Times top / Times attended - Total " + t + " | " + t + " per sec",
        title=title,
        showlegend=legend,
        legend_y=1,
        legend_x=0.9,
    )
    fig.update_layout(general_layout)
    fig.update_traces(textangle=0)
    fig = add_times_top_annotation(fig, df)
    fig = add_clickable_names(fig, df)
    return fig

def add_sorting_options(fig, df, t):
    avg = "Average per m" if isinstance(t(), DeathStat) else "Average per s"
    fig.update_layout(
        updatemenus=[
            dict(
                x=-0.1,
                y=1.06,
                active=0,
                bordercolor='#EEE',
                borderwidth=1,
                bgcolor='#212121',
                showactive=False,
                buttons=[
                    dict(label="Total",
                            method="relayout",
                            args=["yaxis", {"categoryorder": "total ascending", 'showticklabels': False}]),
                    dict(label="Average",
                            method="relayout",
                            args=["yaxis", {"categoryarray": (df.sort_values(by=avg, ascending=True))["Name"],
                                            "categoryorder": "array",
                                            'showticklabels': False}]),
                    dict(label="Times Top",
                            method="relayout",
                            args=["yaxis", {"categoryarray": (df.sort_values(by=["Times Top", f"Total"], ascending=[True, True]))["Name"],
                                            "categoryorder": "array",
                                            'showticklabels': False}]),
                    dict(label="Attendance",
                            method="relayout",
                            args=["yaxis", {"categoryarray": (df.sort_values(by=["Attendance (number of fights)", "Times Top", "Total"], ascending=[True, True, True]))["Name"],
                                            "categoryorder": "array",
                                            'showticklabels': False}]),
                ],
            )
        ]
    )
    return fig


def get_personal_chart(df, y):
    fig = go.Figure()
    for name in df['Name'].unique():
        fig.add_trace(go.Scatter(
            x=df[df['Name']==name]['Date'],
            y=df[df['Name']==name][y],
            mode=df[df['Name']==name]['mode'].iloc[0],
            fill=df[df['Name']==name]['fill'].iloc[0],
            fillcolor='rgba(174, 174, 174, 0.3)',
            name=name,
            line=dict(
                    width=4 if name == df.iloc[0]['Name'] else 1,
                    color=df[df['Name']==name]['Profession_color'].iloc[0] if name == df.iloc[0]['Name'] else 'grey',
                ),
            showlegend=False if name in ['Last Prof', 'First Prof'] else True,
            hoverinfo='skip'
        ))
    

    groups = []
    for i , row in df.iterrows():
        if row['Name'] not in ['Last Prof', 'First Prof']:
            fig.add_trace(go.Scatter(
                x=[row['Date']],
                y=[row[y]],
                mode='markers',
                name=row['Profession'] if str(row['Profession']) != 'nan' else row['Name'],
                text=row['raid_id'],
                legendgroup=row['Profession'],
                marker=(dict(
                    color=row['Profession_color'],
                    size=12,
                    symbol='triangle-up' if str(row['Profession']) != 'nan' else 'circle',
                    line=dict(
                        width=1.5,
                        color='white',
                    )
                )),
                showlegend=True if row['Profession'] not in groups else False,
                hovertemplate=f'{row[y]:,}' if y != 'Sticky' else f'{row[y]}',
                customdata=[row['raid_id']],
            ))
            if row['Profession'] not in groups:
                groups.append(row['Profession']) 

    fig.update_layout(
        title=f"Raid History - {y}",
        showlegend=True,
        legend=dict(
            title='',
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_tickformat='%d-%m-%y',
        yaxis_showline=True,
        yaxis_rangemode='tozero',
        xaxis_gridcolor='grey',
        yaxis_gridcolor='grey',
        yaxis_ticksuffix='%' if y == 'Sticky' else '',
        hovermode='x'
    )
    fig.update_layout(general_layout_line)
    fig.update_layout(dict(margin=dict(r=10)))
    return fig


def get_top_bar_chart_p(df, x, date):
    fig = px.bar(df, y="Name", x=f'{x}', 
                 color="Profession", 
                 text=f'{x}',
                 text_auto=',',
                 title=f'Top 10 - {date}',
                 barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours
                 )
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        showlegend=False,
    )
    fig.update_layout(general_layout)
    fig.update_layout(dict(margin=dict(l=180, r=10)))
    fig.update_traces(textangle=0, width=0.8)
    #fig = add_annotations_graph(fig, df, t)
    fig = add_times_top_annotation(fig, df)
    fig = add_clickable_names(fig, df)
    return fig

def get_logs_line_chart(df):
    fig = px.line(df, x='Date', y='Number', title='Number of unique visits per day')
    fig.update_layout(general_layout_line)
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor='#212121',
            activecolor='#939393'
            
        ),
        tickformatstops = [
            dict(dtickrange=[None, 604800000], value="%e. %b d"),
            dict(dtickrange=[604800000, "M1"], value="%e. %b w"),
            dict(dtickrange=["M1", "M12"], value="%b '%y M"),
            dict(dtickrange=["M12", None], value="%Y Y")
        ]
    )
    fig.update_layout(
        yaxis_showline=True,
        yaxis_rangemode='tozero',
        xaxis_gridcolor='grey',
        yaxis_gridcolor='grey'
    )
    
    return fig


def get_horizontal_bar_chart(df, x, y, title):
    fig = px.bar(df, y=y, x=x, 
                 barmode="relative",
                 orientation='h',
                 title=title,
                 height=1200
                 )
    fig.update_layout(general_layout_line)
    fig.update_layout(
        showlegend=False,
        yaxis_tickfont_size = 10,
        #paper_bgcolor = 'red',
        #plot_bgcolor = 'grey',
    )
    fig.update_layout(dict(margin=dict(l=180, r=10)))
    return fig
