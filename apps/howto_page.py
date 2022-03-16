from click import style
from dash import html, dcc, Output, Input, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc



from app import app

layout = [
    html.H2('How to read the Records of Valhalla', style={'text-align': 'center'}),
    html.Div(
        dbc.Card([
            dbc.CardBody([
                "Welcome to the tutorial on how to read the Records of Valhalla!",
                html.Br(),
                "Since you will be seeing a lot of data, we tried to make a comprehensive guide on the features and usage of our stats page. The goal is to allow everyone to check their own performance over a whole raid at a glance, to see their development over past raids, and to identify top performing players so everyone knows who to ask for advice with a specific class. If you'd prefer to get the tutorial by video, you can find it ",
                html.A("here.", href="https://youtu.be/OLhaHNC1e0M"),
                html.Br(),
                html.Br(),
                dbc.Row([
                    html.Div(id={'type':'larger-img', 'index':1}, style={'z-index': 1}, children='HALLO'),
                    dbc.Col([
                        "First of all, the website will ask you to add an API key with character permissions, so go to your ",
                        html.A("arenanet account", href="https://account.arena.net/applications/create"),
                        " and create a new API key with account and character permissions. We need those to check your character names and show you your own data. Copy the API key and ",
                        html.A("add it", href="https://records-of-valhalla-staging.herokuapp.com/api"),
                        " to the Records of Valhalla. You will then see your account name and a list of your characters. Next to each character, their class and the number of raids they attended is shown. The characters that attended at least one raid are clickable. We will come to that later. You will only need to add your API key once, unless you start playing with a new character. ",
                    ]),
                    dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/API_permissions.png", style={'width': 400, 'margin': 'auto'}), href="assets/API_permissions.png")),
                    dbc.Col(html.Img(id={'type': 'image', 'index': 1},src="assets/API_permissions.png", style={'width': 400, 'margin': 'auto'}, className='bordered-img')),
                ],
#                        justify = "end",
                align="center",
                ),

            dbc.Row([
                dbc.Col("Next in the menu is the Home page. "),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/home.png", style={'width': 400}, className="bordered-img"), href="assets/home.png"), className="centered-col"),
            ],
            align="center",),
                
            dbc.Row([
                dbc.Col("This shows what you have previously known as the Carrot Awards. At the top, there is a dropdown menu where you can choose which raid you want to see the stats of. By default, the last raid will be chosen. Below that, there is a table with a short summary of the raid, like the date, how many kills and deaths we had, the average number of squad members and enemies, the total squad damage, and so on."),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/summary_table.png", style={'width': '95%'}, className="bordered-img"), href="assets/summary_table.png"), className="centered-col"),
            ],
                    align="center"),

            dbc.Row([
                dbc.Col("In the bar charts, the top performing players for the most relevant stats are shown. These stats are damage, tag distance, stability, condition cleanse, healing, and boon rips. Top performing players for damage and tag distance are the top 5, for all other stats on this page it’s the top 3. All except tag distance are sorted by the total values achieved in the chosen raid. Each line shows the name and profession of the character. The classes are also color coded as shown in the legend on the bottom right of each graph. The two numbers at the beginning of each bar indicate how often this character was one of the top performing players and in how many fights they were present. The value at the end of each bar shows the total value achieved over the whole raid, which also corresponds to the length of the bars in the graphs. The value behind the bar is the average stat value per second over all fights a character was involved in. "),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/award_bar_chart.png", style={'width': '60%'}, className="bordered-img"), href="assets/award_bar_chart.png"), className="centered-col")
            ],
            align="center"),

            dbc.Row([
                dbc.Col("For tag distance, the graph looks slightly different. Here, the characters are sorted by the percentage of times they reached top 5 closest to tag. Again, the character name, profession, times top and number of fights in which a character was involved are given. The percentage at the end of the bar indicates how often a character achieved top 5 distance to tag in the fights they were involved in, so times top 5 divided by number of fights present."),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/distance_bar_chart.png", style={'width': '60%'}, className="bordered-img"), href="assets/distance_bar_chart.png"), className="centered-col")
            ],
                    align="center"),

            dbc.Row([
                dbc.Col("Next up are Details. "),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/details.png", style={'width': 400}, className="bordered-img"), href="assets/details.png"), className="centered-col")
            ],
                    align="center"),

            dbc.Row(
                dbc.Col([
                    "Again, you can choose from which raid you would like to see stats using the drop down menu at the top, which by default is the last raid. You will see a short summary of the overall squad stats for the chosen raid in a table. Below that, you see tabs for different stats, namely Damage, Rips, Might, Fury, Healing, Barrier, Cleanses, Stability, Protection, Aegis, and Distance. The numbers shown in these bar charts are the same as those shown on the Home page, i.e. times top, attendance, total value and average value per second (or percentage times top for distance). Note that for your healing or barrier to register, you will need to have the ",
                    dbc.CardLink("arcdps healing addon", href="https://github.com/Krappa322/arcdps_healing_stats/releases"),
                    " running and stats sharing enabled. The top performing players will be shown by name. For might and fury, these are only the top 2 players, for all other stats you haven’t seen on the Home page yet it’s the top 3 players. All other players are shown by their profession only. ",
                    html.Br(),
                    "Additionally, you will be able to see your own character name if you were there for the chosen raid. This way, you can compare yourself to the top performing players, but can also see how you are doing compared to others in your class, using the color coding or profession names. If you want to see only players of specific classes, you can enable or disable them by clicking on the corresponding legend items. You can also view only players of a single class by double clicking the corresponding legend item.",
                ])
            ),

            dbc.Row([
                dbc.Col("On the top left, there is a drop down menu to sort the graphs differently. The choices are: 'total', which is the default and means the total stat value achieved over the whole raid; 'average', which is the average stat value per second over all fights a character was involved in; 'times top', which indicates how often someone achieved top stats; and 'attendance', which is how many fights someone was there for. Using this, you can for example check how you were doing compared to others on average, if you weren’t able to attend the whole raid."),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/sorting_order.png", style={'width': "70%"}, className="bordered-img"), href="assets/sorting_order.png"), className="centered-col")
            ],
                    align="center"),

            dbc.Row(
                dbc.Col("Now we get to your personal profile. You can get to it either by")
                ),
            dbc.Row([
                dbc.Col("clicking on one of your character names on the API page ", className="centered-col"),
                dbc.Col("or clicking one of your character names in any of the graphs ", className="centered-col"),
                dbc.Col("or by clicking on your account name and then Profile. ", className="centered-col")
            ]),
            dbc.Row([
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/profile_from_api.png", style={'width': 600}, className="bordered-img"), href="assets/profile_from_api.png"), className="centered-col"),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/profile_from_graph.png", style={'width': 600}, className="bordered-img"), href="assets/profile_from_graph.png"), className="centered-col"),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/profile_from_prof.png", style={'width': 200}, className="bordered-img"), href="assets/profile_from_prof.png"), className="centered-col"),
            ]),

            dbc.Row([
                dbc.Col("At the top, you see a summary table of how many raids and how many fights this character attended, how many fights you missed if you weren’t there for a whole raid, and how often you achieved top stats in a chosen stat. Below that is a drop down menu showing all of your characters that were present for at least one raid. "),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/profile_overview.png", className="bordered-img"), href="assets/profile_overview.png"), className="centered-col"),
            ],
                    align="center"),

            dbc.Row([
                dbc.Col([
                    "The line chart gives you your stat history over the past raids. You can choose which stat you want to see using the radio buttons in the table at the bottom. Here, we show your average stats, since these are more comparable between raids than total stats. Keep in mind that these values still depend on what kind of fights we had, for example how many enemies there were and if it was an organized group. The colored line shows your own average stats. The white line shows the top average stats for each raid, which might come from a different person every time. The colored markers indicate which class generated the top average stats.",
                    html.Br(),
                    "The shaded gray region shows the highest and lowest average stats in your profession. Note again that for healing and barrier, only players running the healing addon will register, so the lowest will often be zero for these two stats and thus the shaded region will go down to zero.",
                    html.Br(),
                    "If you want to look at something more closely, you can draw a rectangle in the chart to zoom in on that part, which might be interesting for stats to which your class is not a main contributor, for example boon rips on scrapper or stability on scourge. To reset the graph, double click anywhere in the graph area."
                ]),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/line_chart_annotated.png", style={'width': "80%"}, className="bordered-img"), href="assets/line_chart_annotated.png"), className="centered-col"),
            ],
                    align="center"),

            dbc.Row([
                dbc.Col("If you hover over any of the data points, you will see the top 10 average stats as a bar chart on the right, where the top performing players and your own characters are shown by name. "),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/hover_bar_chart.png", style={'width': "80%"}, className="bordered-img"), href="assets/hover_bar_chart.png"), className="centered-col"),
            ],
                    align="center"),

            dbc.Row([
                dbc.Col("The table at the bottom shows your average stats for each raid in numbers, if you want to look at several stats at once. You can also enable and disable showing some raids in the line chart by ticking the checkboxes at the left of the table."),
                dbc.Col(dbc.CardLink(dbc.CardImg(src="assets/profile_table.png", style={'width': "80%"}, className="bordered-img"), href="assets/profile_table.png"), className="centered-col"),
            ],
                    align="center"),

            dbc.Row(dbc.Col("We hope this covers the basics and this tool will be helpful for everyone. Let us know if there are any questions! Thank you :)", className="centered-col"))
                
        ])#, style={'text-align': 'left'})
        ])
    )

]

@app.callback(
    Output({'type': 'image', 'index': MATCH}, 'style'),
    Input({'type': 'image', 'index': MATCH}, 'n_clicks'),
    State({'type': 'image', 'index': MATCH}, 'style'),
    prevent_initial_call=True
)
def enlarge_image_on_click(n, style):
    newstyle = {
        'z-index': 1,
        'position': 'fixed',
        'left': '25%',
        'top': '25%',
        'width': '50%'
    }
    oldstyle = {
        'width': '400',
        'margin': 'auto'
    }
    print(style)
    if n:
        if style == oldstyle:
            return newstyle
        else:
            return oldstyle


#login = dbc.Row([
#    dcc.Location(id='url_login', refresh=True),
#    dbc.Col([
#        html.H2('Login Form', style={'text-align': 'center'}),
#        dbc.Card([
#            dbc.CardImg(src="assets/logo.png", top=True, style={'width': 200, 'margin': 'auto'}),
#            dbc.CardBody([
#                html.Div(
#                    className='mb-3',
#                    children=[
#                        dbc.Input(type='text', id='uname-box', placeholder='Enter your username')
#                    ]
#                ),
#                html.Div(
#                    className='mb-3',
#                    children=[
#                        dbc.Input(type='password', id='pwd-box', placeholder='Enter your password')
#                    ]
#                ),
#                dbc.Button('Login', id='login-button', class_name='btn btn-color px-5 w-100', n_clicks=0)
#            ])
#        ]),
#        html.Div(children='', id='output-state')
#    ],
#    width={'size': 4, 'offset': 4})
#])
#
#
## Successful login
#success = html.Div([html.Div([html.H2('Login successful.'),
#                              html.Br(),
#                              dcc.Link('Home', href='/')])
#                    ])
#
## Failed Login
#failed = html.Div([html.Div([html.H2('Log in Failed. Please try again.'),
#                             html.Br(),
#                             html.Div([login]),
#                             dcc.Link('Home', href='/')
#                             ])
#                   ])
#
#
## Logout
#logout = html.Div([html.Div(html.H2('You have been logged out - Please login')),
#                   html.Br(),
#                   dcc.Link('Home', href='/')
#                   ])
#
#
#logged_in_menu = dbc.Nav(className='menu', children=[
#    dbc.DropdownMenu(
#            [dbc.DropdownMenuItem("API Key", href='/api'), 
#            dbc.DropdownMenuItem("Profile", href='/details/')],
#            label="Account",
#            caret=False,
#            nav=True,
#            id='account-dpn',
#        ),
##    dbc.NavItem(dbc.NavLink("Home", href='/')),
##    dbc.NavItem(dbc.NavLink("Details", href='/details')),
#    dbc.NavItem(dbc.NavLink("Upload", href='/upload')),
#    dbc.NavItem(dbc.NavLink("Logout", href='/logout')),
#],
#)
#
#loggin_menu = dbc.Nav(className='menu', children=[
#    dbc.DropdownMenu(
#            [dbc.DropdownMenuItem("API Key", href='/api'), 
#            dbc.DropdownMenuItem("Profile", href='/details/')],
#            label="Account",
#            caret=False,
#            nav=True,
#            id='account-dpn',
#        ),
##    dbc.NavItem(dbc.NavLink("Home", href='/')),
##    dbc.NavItem(dbc.NavLink("Details", href='/details')),
##    dbc.NavItem(dbc.NavLink("Admin", href='/login')),
#])
#
#
#@app.callback(Output('url_login', 'pathname'),
#              Output('output-state', 'children'),
#              [Input('login-button', 'n_clicks')],
#              [State('uname-box', 'value'), State('pwd-box', 'value')])
#def login_button_click(n_clicks, username, password):
#    if n_clicks > 0:
#        #user = db.session.query(User).filter_by(username = username).first()
#        #if user is not None:
#        #    if check_password_hash(user.password, password):
#        #        login_user(user)
#        #        return '/success', ''
#        #    else:
#        #        return '/login', 'Incorrect username or password'
#        #else:
#        #    return '/login', 'Incorrect username or password'
#        return '/success', ''
#    return '/login', ''
#
#
#@app.callback(
#    Output('user-status-div', 'children'), 
#    Output('login-status', 'data'), 
#    [Input('url', 'pathname')]
#    )
#def login_status(url):
#    ''' callback to display login/logout link in the header '''
#    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated \
#            and url != '/logout':  # If the URL is /logout, then the user is about to be logged out anyways
#        return logged_in_menu, current_user.get_id()
#    else:
#        return loggin_menu, 'loggedout'
