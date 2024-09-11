# Import library dependencies.
from dash import Dash, html, dash_table, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
from pathlib import Path
from dotenv import load_dotenv
import os

# Import project python file dependencies.
from dashboard_data_parser import *
from honeypy import *

# Constants.
base_dir = Path(__file__).parent.parent
creds_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'creds_audits.log'
cmd_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'cmd_audits.log'
dotenv_path = Path('public.env')
load_dotenv(dotenv_path=dotenv_path)

creds_audits_log_df = parse_creds_audits_log(creds_audits_log_local_file_path)
cmd_audits_log_df = parse_cmd_audits_log(cmd_audits_log_local_file_path)

top_ip_address = top_10_calculator(creds_audits_log_df, "ip_address")
top_usernames = top_10_calculator(creds_audits_log_df, "username")
top_passwords = top_10_calculator(creds_audits_log_df, "password")
top_cmds = top_10_calculator(cmd_audits_log_df, "Command")

# New Theme: MINTY (Bootstrap theme)
load_figure_template(["minty"])
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css")

# HONEYPY Logo and Favicon
image = 'assets/images/honeypot4.png'

# Declare Dash App with MINTY theme
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc_css])
app.title = "HONEYPY"
app._favicon = "../assets/images/honeypy-favicon.ico"

country = os.getenv('COUNTRY')

# Country Lookup
def country_lookup(country):
    if country == 'True':
        get_ip_to_country = ip_to_country_code(creds_audits_log_df)
        top_country = top_10_calculator(get_ip_to_country, "Country_Code")
        message = dbc.Col(dcc.Graph(figure=px.bar(top_country, x="Country_Code", y='count', 
                                                  color_discrete_sequence=["#FF7F0E"]), 
                                                  style={"height": "300px"}), style={'width': '33%', 'display': 'inline-block'})
    else:
        message = "No Country Panel Defined"
    return message

# Update Graphs: Resize and add color changes
fig_ip = px.bar(top_ip_address, x="ip_address", y='count', color_discrete_sequence=["#1F77B4"])
fig_ip.update_layout(margin=dict(l=20, r=20, t=30, b=30), height=250)

fig_username = px.bar(top_usernames, x='username', y='count', orientation='h', color_discrete_sequence=["#FF7F0E"])
fig_username.update_layout(margin=dict(l=20, r=20, t=30, b=30), height=250)

fig_password = px.bar(top_passwords, x='password', y='count', color_discrete_sequence=["#2CA02C"])
fig_password.update_layout(margin=dict(l=20, r=20, t=30, b=30), height=250)

fig_cmd = px.bar(top_cmds, x='Command', y='count', color_discrete_sequence=["#D62728"])
fig_cmd.update_layout(margin=dict(l=20, r=20, t=30, b=30), height=250)

# Updated Tables: Light color scheme with padding/margins
tables = html.Div([
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    data=creds_audits_log_df.to_dict('records'),
                    columns=[{"name": "IP Address", 'id': 'ip_address'}],
                    style_table={'width': '100%', 'color': 'black', 'padding': '10px'},
                    style_cell={'textAlign': 'left', 'color': '#2C3E50'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#3498DB', 'color': 'white'},
                    page_size=10
                ),
            ),
            dbc.Col(
                dash_table.DataTable(
                    data=creds_audits_log_df.to_dict('records'),
                    columns=[{"name": "Usernames", 'id': 'username'}],
                    style_table={'width': '100%', 'padding': '10px'},
                    style_cell={'textAlign': 'left', 'color': '#2C3E50'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#3498DB', 'color': 'white'},
                    page_size=10
                ),
            ),
            dbc.Col(
                dash_table.DataTable(
                    data=creds_audits_log_df.to_dict('records'),
                    columns=[{"name": "Passwords", 'id': 'password'}],
                    style_table={'width': '100%', 'padding': '10px'},
                    style_cell={'textAlign': 'left', 'color': '#2C3E50'},
                    style_header={'fontWeight': 'bold', 'backgroundColor': '#3498DB', 'color': 'white'},
                    page_size=10
                ),
            ),       
        ])
])

apply_table_theme = html.Div(
    [tables],
    className="dbc"
)

# Navigation bar at the top with project name "HoneyLogix"
navbar = dbc.NavbarSimple(
    brand="HoneyLogix",
    brand_href="#",
    color="primary",
    dark=True,
    fluid=True,
    className="mb-4"
)

# Updated layout with new color scheme, fonts, graph sizes, and shapes
app.layout = dbc.Container([
    # Navbar at the top
    navbar,
    
    # Title with logo
    html.Div([html.Img(src=image, style={'height': '20%', 'width': '20%'})], style={'textAlign': 'center'}, className='dbc'),
    
    # Row 1: IP, Username, Password Charts with updated sizes and colors
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_ip), width=4),
        dbc.Col(dcc.Graph(figure=fig_username), width=4),
        dbc.Col(dcc.Graph(figure=fig_password), width=4),
    ], align='center', class_name='mb-4'),

    # Row 2: Top Commands and Country Codes
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_cmd), style={'width': '33%', 'display': 'inline-block'}),
        country_lookup(country)
    ], align='center', class_name='mb-4'),

    # Table Titles
    html.Div([
        html.H3(
            "Intelligence Data", 
            style={'textAlign': 'center', "font-family": 'Arial, sans-serif', 'font-weight': 'bold', 'color': '#2C3E50'}, 
        ),
    ]),

    # Row 3: Data Tables
    apply_table_theme    
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
