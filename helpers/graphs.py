import plotly.express as px

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


def get_top_bar_chart(df, t):
    fig = px.bar(df, y="Name", x="Total " + t, color="Profession", text="Total "+ t, barmode="relative",
                 orientation='h',
                 color_discrete_map=profession_colours)
    fig.update_layout(
        yaxis_categoryorder='total ascending',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#EEE',
        title="Top " + t,
        showlegend=False,
    )
    fig = add_annotations_graph(fig, df, t)
    return fig


def add_annotations_graph(fig, df, t):
    for name in df["Name"]:
        fig.add_annotation(y=name, x=int(df[df["Name"] == name]["Total " + t].values[0]),
                           text="{:.2f}".format(df[df["Name"] == name]["Average " + t + " per s"].values[0]),
                           showarrow=False,
                           yshift=0,
                           xshift=0,
                           xanchor="left"),
        fig.add_annotation(y=name, x=0,
                           text=" " + str(int(df[df["Name"] == name]["Times Top"].values[0]))
                                + " / " +
                                str(int(df[df["Name"] == name]["Attendance (number of fights)"].values[0])),
                           showarrow=False,
                           yshift=0,
                           xshift=0,
                           xanchor="left",
                           )

    return fig
