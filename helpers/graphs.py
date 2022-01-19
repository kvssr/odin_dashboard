import pandas as pd
from pandas.core.frame import DataFrame
import plotly.express as px

from app import db
from models import Fight, FightSummary, Profession
import dash_bootstrap_components as dbc
from dash import html

profession_colours = {
    'Guardian': '#186885',
    'Dragonhunter': '#186885',
    'Firebrand': '#186885',
    'Revenant': '#661100',
    'Herald': '#661100',
    'Renegade': '#661100',
    'Warrior': '#CAAA2A',
    'Berserker': '#CAAA2A',
    'Spellbreaker': '#CAAA2A',
    'Engineer': '#87581D',
    'Scrapper': '#87581D',
    'Holosmith': '#87581D',
    'Ranger': '#67A833',
    'Druid': '#67A833',
    'Soulbeast': '#67A833',
    'Thief': '#974550',
    'Daredevil': '#974550',
    'Deadeye': '#974550',
    'Elementalist': '#DC423E',
    'Tempest': '#DC423E',
    'Weaver': '#DC423E',
    'Mesmer': '#69278A',
    'Chronomancer': '#69278A',
    'Mirage': '#69278A',
    'Necromancer': '#2C9D5D',
    'Reaper': '#2C9D5D',
    'Scourge': '#2C9D5D',
}

profession_shorts = {
    'Guardian': 'Gnd',
    'Dragonhunter': 'Dgh',
    'Firebrand': 'Fbd',
    'Revenant': 'Rev',
    'Herald': 'Her',
    'Renegade': 'Ren',
    'Warrior': 'War',
    'Berserker': 'Brs',
    'Spellbreaker': 'Spb',
    'Engineer': 'Eng',
    'Scrapper': 'Scr',
    'Holosmith': 'Hls',
    'Ranger': 'Rgr',
    'Druid': 'Dru',
    'Soulbeast': 'Slb',
    'Thief': 'Thf',
    'Daredevil': 'Dar',
    'Deadeye': 'Ded',
    'Elementalist': 'Ele',
    'Tempest': 'Tmp',
    'Weaver': 'Wea',
    'Mesmer': 'Mes',
    'Chronomancer': 'Chr',
    'Mirage': 'Mir',
    'Necromancer': 'Nec',
    'Reaper': 'Rea',
    'Scourge': 'Scg',
}

raid_types = {
    'morning',
    'afternoon',
    'guild',
    'unknown'
}

general_layout = {
        'title_xanchor':'center',
        'title_x':0.5,
        'legend_y':0,
        'legend_x':0.9,
        'margin':dict(l=200),
        'font_size':13,
        'yaxis_title':'',
        'paper_bgcolor':'rgba(0,0,0,0)',
        'plot_bgcolor':'rgba(0,0,0,0)',
        'font_color':'#EEE',
        'yaxis_automargin': False,
        'yaxis_ticksuffix': ' ',
        'yaxis_tickfont_size': 15
}

def get_top_bar_chart(df, t, title, legend = True):
    fig = px.bar(df, y="Name", x="Total " + t, 
                 color="Profession", 
                 text="Total "+ t,
                 text_auto=',',
                 barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours
                 )
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        xaxis_title="Times top / Times attended - Total " + t + " | " + t + " per sec",
        title=title,
        showlegend=legend,
    )
    fig.update_layout(general_layout)
    fig.update_traces(textangle=0)
    fig = add_annotations_graph(fig, df, t)
    fig = add_times_top_annotation(fig, df)
    return fig


def add_annotations_graph(fig, df, t):
    for name in df["Name"]:
        if t != 'deaths':
            fig.add_annotation(y=name, x=int(df[df["Name"] == name]["Total " + t].values[0]),
                               text="{:,.0f}".format(df[df["Name"] == name]["Average " + t + " per s"].values[0]) if t in ['dmg', 'heal', 'barrier', 'dmg_taken'] else "{:,.2f}".format(df[df["Name"] == name]["Average " + t + " per s"].values[0]),
                               showarrow=False,
                               yshift=0,
                               xshift=2,
                               xanchor="left",
                               font_size=13,
            )
    return fig


def get_top_dist_bar_chart(df, legend=True):
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
        title="Top Closest To Tag",
    )
    fig.update_layout(general_layout)
    fig = add_times_top_annotation(fig, df)


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
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm', id='summary')
            return [table, html.Hr()]
        return None
    except Exception as e:
        db.session.rollback()
        print(e)
        return None


def get_top_dmg_taken_chart(df, t, title, legend = True):
    fig = px.bar(df, y=df["Name"], x=df["Total dmg_taken"], 
                 color=df["Name"],
                 hover_name="Name",
                 text=df['Profession'],
                 text_auto=',',
                 barmode="relative",
                 orientation='h',
                 color_discrete_sequence=df["Profession_color"].values
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

    for name in df['Name']:
        fig.add_annotation(y=name, x=int(df[df["Name"] == name]["Total dmg_taken"].values[0]),
                                text="{:,.0f}".format(df[df["Name"] == name]["Average dmg_taken per s"].values[0]),
                                showarrow=False,
                                yshift=0,
                                xshift=2,
                                xanchor="left",
                                font_size=13,
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
    return fig



