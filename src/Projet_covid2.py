import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
import datetime


# DATA
url = 'https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv'
df1 = pd.read_csv('C:/Users/dejon/OneDrive/Desktop/df_clean.csv')
df = pd.read_csv(url) # il s'agit de la cumulation des cas et gueris par pays 


a = df[df.maille_nom == 'France']
a = a[["date","cas_confirmes","deces","gueris"]]
a = a.melt(id_vars="date")
fig = px.line(a, x = 'date', y = 'value', color = 'variable')



# App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app= dash.Dash("Dashboard", external_stylesheets=external_stylesheets)


# couleur de fond et du texte (on peut trouver les couleurs qu'on veut sur : https://htmlcolors.com/)
colors = {
    'background': '#B9B2B0',
    'text': '#3D3B3A',
    'grid': '#333333',
    'red': '#BF0000',
    'blue': '#466fc2',
    'green': '#5bc246'
}


# layout
app.layout = html.Div([
    dcc.Tabs(id="tabs-styled-with-props", value='tab-1',style = {'fontWeight': 'bold','backgroundColor': colors['background']}, children=[
        dcc.Tab(label='Statistiques descriptives', value='tab-1'),
        dcc.Tab(label='Modelisation SEAIRD', value='tab-2'),
    ], colors={
        "border": "black",
        "primary": "gold",
        "background": "#9CA09C"
    }),
    html.Div(id='tabs-content-props')
])

@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))

def render_content(tab):
	#============================================================== TAB 1
	if tab == 'tab-1':
		return html.Div(style={'backgroundColor': colors['background']}, children=[
	html.H1(style={'textAlign': 'center', 'color': colors['text'],'fontWeight': 'bold'},children="Projet Covid"),
	html.Div(className = 'row',style={'textAlign': 'center', 'color': colors['text'],'fontWeight': 'bold'}, children = [
		# choix entre pays, regions ou departements
		dcc.RadioItems(
			id = 'choix_de_visualisation',
			options = [
				{'label':"Departement","value":'dep_name'},
				{'label':"Region","value":'region_name'}
			],
			value = 'region_name',
			labelStyle={'display': 'inline-block'}
		),
		# choix multiple de region ou de departements en fonction de ce qui a ete choisi au radioitem ci dessus
		dcc.Dropdown(
			id = 'noms_regions_dep',
			options = [],
			multi = True,
			placeholder = "Selection simple ou multiples"
		),
	]),
	# Indicateurs
	html.Div(		
		style={
			'textAlign': 'center',
			'color': colors['red'],
			'width': '25%',
			'display': 'inline-block'
		},
		children =[dcc.Graph(id='recovered_ind'), ]),
	html.Div(
		style={
			'textAlign': 'center',
			'color': colors['red'],
			'width': '25%',
			'display': 'inline-block'
		},
		children =[dcc.Graph(id='death_ind'), ]),
	html.Div(
		style={
			'textAlign': 'center',
			'color': colors['red'],
			'width': '25%',
			'display': 'inline-block'
		},
		children =[dcc.Graph(id='hospitalises_ind'), ]
	),
	html.Div(
		style={
			'textAlign': 'center',
			'color': colors['red'],
			'width': '25%',
			'display': 'inline-block'
		},
		children =[dcc.Graph(id='asymptomatique_ind'), ]
	),
	# graph 1
	html.Div(
		style={
			'width': '13%',
			'margin-left': '7%',
			'fontWeight': 'bold',
			'display': 'inline-block'
		},
		children =[
			dcc.RadioItems(
				id = 'choix_de_variable',
				options = [
					{'label':"Deces","value":'deces'},
					{'label':"Hospitalises","value":'hospitalises'},
					{'label':"Gueris","value":'gueris'},
					{'label':"Cas de Covid","value":'total'}
				],
				value = 'deces',
				style={
					'margin-bottom': '15%',
					'line-height': '1.2'
				},
			),
		]
	),
	html.Div(
		style={
			'width': '80%',
			'display': 'inline-block'
		},
		children = [dcc.Graph(id = 'plot1', figure = fig), ]
	),
	# Graph 2
	html.Div(
		style={
			'width': '50%',
			'display': 'inline-block'
		},
		children = [dcc.Graph(id = 'plot6', figure = fig), ]
	),
])

























	#============================================================== TAB 2
	elif tab == 'tab-2':
		return html.Div([
		html.H3('Tab content 2')
		])




	#============================================================== callback du TAB 1
	
	
# call back : je veux que pour le choix de dropdown "noms_regions_dep", ca change en fonction de l'item selectionner dans le radioitem "choix de visualisation"
@app.callback(
	Output('noms_regions_dep','options'),
	[Input('choix_de_visualisation','value')]
)

def update_dropdown(choix1):
	data = df1
	return [{'label': i, 'value': i} for i in data[str(choix1)].unique()]


# call back plot1 : je veux un graph avec le nombre de personnes infectees cumulees au fil du temps en fonction des departements ou des regions choisies
@app.callback(
	Output('plot1','figure'),
	[Input('noms_regions_dep','value'),
	Input('choix_de_variable','value')]
)

def update_plot1(zones_a_ploter,nom_variable):
	if zones_a_ploter == 'NoneType':
		zones_a_ploter = ['Hauts-de-France']
	liste = list(zones_a_ploter)
	a = df1[df1['region_name'].isin(liste)]
	a = a[['date',str(nom_variable),'region_name']]
	a = a.pivot_table(index='date',columns='region_name',values = str(nom_variable ),aggfunc='sum')
	a = a.reset_index()
	a = a.melt(id_vars= 'date')
	
	if len(a) == 0:
		a = df1[df1['dep_name'].isin(liste)]
		a = a[['date',str(nom_variable),'dep_name']]
		a = a.pivot_table(index='date',columns='dep_name',values = str(nom_variable ),aggfunc='sum')
		a = a.reset_index()
		a = a.melt(id_vars= 'date')

	if nom_variable == 'total':
		titre = 'Nombre de cas de covid pour 100 000 habitants'
	if nom_variable == 'deces':
		titre = 'Nombre de deces par le virus pour 100 000 habitants'
	if nom_variable == 'gueris':
		titre = 'Nombre de guerison du virus pour 100 000 habitants'
	if nom_variable == 'hospitalises':
		titre = "Nombre d'hospitalises a cause du virus pour 100 000 habitants"
	
	fig = px.line(a, x = 'date', y = 'value', color = a.columns[1] , title = titre)

	return fig


# call back plot2,3,4: je veux un graph avec le nombre de personnes infectees, geries, et decedes cumulees au fil du temps
@app.callback(
	Output('recovered_ind','figure'),
	[Input('noms_regions_dep','value')]
)

def update_plot2(zones_a_ploter):
	liste = list(zones_a_ploter)
	a = df1[df1['region_name'].isin(liste)]
	nom_variable = 'region_name'
	if len(a) == 0: # en gros si mon dataframe possede 0 lignes, cela veut dire que la liste contient des noms de departement et qu'il faut donc regarder dans la colonne des departements
		a = df1[df1['dep_name'].isin(liste)]
		nom_variable = 'dep_name'
	a = a[["date","hospitalises","deces","gueris","total","region_name","dep_name"]]
	# nombre de gueris
	b = a[a['date'] == a.date.unique()[-1]]
	lieu = b.groupby(nom_variable)
	value = lieu['gueris'].agg(np.mean)
	value = int(value.mean())
	# delta
	c = a[a['date'] == a.date.unique()[-2]]
	lieu = c.groupby(nom_variable)
	delta = lieu['gueris'].agg(np.mean)
	delta = int(delta.mean())

	return {
		'data': [{
			'type': 'indicator',
			'mode': 'number+delta',
			'value': value,
			'delta': {
				'reference': delta,
				'valueformat': ',g',
				'relative': False,
				'increasing': {'color': colors['blue']},
				'decreasing': {'color': colors['green']},
				'font': {'size': 25}},
			'number': {'valueformat': ',',
			      'font': {'size': 50}},
			'domain': {'y': [0, 1], 'x': [0, 1]}
			}],
		'layout': go.Layout(
			title={'text': "PERSONNES GUERIES (/100 000 hab)"},
			font=dict(color=colors['red']),
			paper_bgcolor=colors['background'],
			plot_bgcolor=colors['background'],
			height=200
		)
	}


@app.callback(
	Output('death_ind','figure'),
	[Input('noms_regions_dep','value')]
)

def update_plot3(zones_a_ploter):
	liste = list(zones_a_ploter)
	a = df1[df1['region_name'].isin(liste)]
	nom_variable = 'region_name'
	if len(a) == 0: # en gros si mon dataframe possede 0 lignes, cela veut dire que la liste contient des noms de departement et qu'il faut donc regarder dans la colonne des departements
		a = df1[df1['dep_name'].isin(liste)]
		nom_variable = 'dep_name'
	a = a[["date","hospitalises","deces","gueris","total","region_name","dep_name"]]
	# nombre de deces
	b = a[a['date'] == a.date.unique()[-1]]
	lieu = b.groupby(nom_variable)
	value = lieu['deces'].agg(np.mean)
	value = int(value.mean())
	# delta
	c = a[a['date'] == a.date.unique()[-2]]
	lieu = c.groupby(nom_variable)
	delta = lieu['deces'].agg(np.mean)
	delta = int(delta.mean())
	return {
		'data': [{
			'type': 'indicator',
			'mode': 'number+delta',
			'value': value,
			'delta': {
				'reference': delta,
				'valueformat': ',g',
				'relative': False,
				'increasing': {'color': colors['blue']},
				'decreasing': {'color': colors['green']},
				'font': {'size': 25}},
			'number': {'valueformat': ',',
			      'font': {'size': 50}},
			'domain': {'y': [0, 1], 'x': [0, 1]}
			}],
		'layout': go.Layout(
			title={'text': "DECES TOTAL (/100 000 hab)"},
			font=dict(color=colors['red']),
			paper_bgcolor=colors['background'],
			plot_bgcolor=colors['background'],
			height=200
		)
	}

@app.callback(
	Output('hospitalises_ind','figure'),
	[Input('noms_regions_dep','value')]
)

def update_plot4(zones_a_ploter):
	liste = list(zones_a_ploter)
	a = df1[df1['region_name'].isin(liste)]
	nom_variable = 'region_name'
	if len(a) == 0: # en gros si mon dataframe possede 0 lignes, cela veut dire que la liste contient des noms de departement et qu'il faut donc regarder dans la colonne des departements
		a = df1[df1['dep_name'].isin(liste)]
		nom_variable = 'dep_name'
	a = a[["date","hospitalises","deces","gueris","total","region_name","dep_name"]]
	# nombre de hospitalises
	b = a[a['date'] == a.date.unique()[-1]]
	lieu = b.groupby(nom_variable)
	value = lieu['hospitalises'].agg(np.mean)
	value = int(value.mean())
	# delta
	c = a[a['date'] == a.date.unique()[-2]]
	lieu = c.groupby(nom_variable)
	delta = lieu['hospitalises'].agg(np.mean)
	delta = int(delta.mean())
	return {
		'data': [{
			'type': 'indicator',
			'mode': 'number+delta',
			'value': value,
			'delta': {
				'reference': delta,
				'valueformat': ',g',
				'relative': False,
				'increasing': {'color': colors['blue']},
				'decreasing': {'color': colors['green']},
				'font': {'size': 25}},
			'number': {'valueformat': ',',
			      'font': {'size': 50}},
			'domain': {'y': [0, 1], 'x': [0, 1]}
			}],
		'layout': go.Layout(
			title={'text': "HOSPITALISES (/100 000 hab)"},
			font=dict(color=colors['red']),
			paper_bgcolor=colors['background'],
			plot_bgcolor=colors['background'],
			height=200
		)
	}


@app.callback(
	Output('asymptomatique_ind','figure'),
	[Input('noms_regions_dep','value')]
)

def update_plot5(zones_a_ploter):
	liste = list(zones_a_ploter)
	a = df1[df1['region_name'].isin(liste)]
	nom_variable = 'region_name'
	if len(a) == 0: # en gros si mon dataframe possede 0 lignes, cela veut dire que la liste contient des noms de departement et qu'il faut donc regarder dans la colonne des departements
		a = df1[df1['dep_name'].isin(liste)]
		nom_variable = 'dep_name'
	a = a[["date","hospitalises","deces","gueris","asymptomatiques","region_name","dep_name"]]
	# nombre de asymptomatiques
	b = a[a['date'] == a.date.unique()[-1]]
	lieu = b.groupby(nom_variable)
	value = lieu['asymptomatiques'].agg(np.mean)
	value = int(value.mean())
	# delta
	c = a[a['date'] == a.date.unique()[-2]]
	lieu = c.groupby(nom_variable)
	delta = lieu['asymptomatiques'].agg(np.mean)
	delta = int(delta.mean())
	return {
		'data': [{
			'type': 'indicator',
			'mode': 'number+delta',
			'value': value,
			'delta': {
				'reference': delta,
				'valueformat': ',g',
				'relative': False,
				'increasing': {'color': colors['blue']},
				'decreasing': {'color': colors['green']},
				'font': {'size': 25}},
			'number': {'valueformat': ',',
			      'font': {'size': 50}},
			'domain': {'y': [0, 1], 'x': [0, 1]}
			}],
		'layout': go.Layout(
			title={'text': "ASYMPTOMATIQUES (/100 000 hab)"},
			font=dict(color=colors['red']),
			paper_bgcolor=colors['background'],
			plot_bgcolor=colors['background'],
			height=200
		)
	}

# Ici c'est pour le plot en bar
@app.callback(
	Output('plot6','figure'),
	[Input('noms_regions_dep','value'),
	Input('choix_de_variable','value')]
)

def update_plot6(zones_a_ploter,nom_variable):
	liste = list(zones_a_ploter)
	a = df1[df1['region_name'].isin(liste)]
	a = a[['date',str(nom_variable),'region_name']]
	a = a.pivot_table(index='date',columns='region_name',values = str(nom_variable ),aggfunc='sum')
	a = a.reset_index()
	a = a.melt(id_vars= 'date')

	if len(a) == 0:
		a = df1[df1['dep_name'].isin(liste)]
		a = a[['date',str(nom_variable),'dep_name']]
		a = a.pivot_table(index='date',columns='dep_name',values = str(nom_variable ),aggfunc='sum')
		a = a.reset_index()
		a = a.melt(id_vars= 'date')

	a = a[a.date == a.date.unique()[-1]]
	
	if nom_variable == 'total':
		titre = "Nombre de cas de covid pour 100 000 habitants au " + str(a.date.unique()[-1])
	if nom_variable == 'deces':
		titre = 'Nombre de deces par le virus pour 100 000 habitants au ' + str(a.date.unique()[-1])
	if nom_variable == 'gueris':
		titre = 'Nombre de guerison du virus pour 100 000 habitants au ' + str(a.date.unique()[-1])
	if nom_variable == 'hospitalises':
		titre = "Nombre d'hospitalises pour 100 000 habitants au " + str(a.date.unique()[-1])
	
	fig = px.bar(a, x = a.columns[1],y = 'value' , title = str(titre))
	return fig






	#============================================================== callback du TAB 2




































if __name__ == '__main__':
	app.run_server(debug=True)
