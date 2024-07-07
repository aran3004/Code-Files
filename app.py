import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import gspread

# Google Sheets setup
sa = gspread.service_account(
    filename='sensing-and-iot-project-697ae27b6369.json')
sh = sa.open("Sensing IoT Data")
wks = sh.worksheet("Data2")
data = wks.get_all_records()
df = pd.DataFrame(data)

df['Ideal Temp'] = ((df['Sensor Temp (°C)'] >= 18) &
                    (df['Sensor Temp (°C)'] <= 21)).astype(int)
df['Ideal Humidity'] = ((df['Sensor Humidity (%)'] >= 40) &
                        (df['Sensor Humidity (%)'] <= 60)).astype(int)
# Calculate the percentage of time in the ideal temperature and humidity ranges
temp_percentage = (df['Ideal Temp'].mean()) * 100
humidity_percentage = (df['Ideal Humidity'].mean()) * 100
df['Ideal Temp & Humidity'] = df['Ideal Temp'] * df['Ideal Humidity']
ideal_percentage = (df['Ideal Temp & Humidity'].mean()) * 100


# Assuming you're calculating on 'Sensor Temp (°C)' with a window size of 20
window_size = 20

# Calculate SMA (Simple Moving Average)
df['SMA'] = df['Sensor Temp (°C)'].rolling(window=window_size).mean()

# Calculate EMA (Exponential Moving Average)
df['EMA'] = df['Sensor Temp (°C)'].ewm(span=window_size, adjust=False).mean()


def calculate_bollinger_bands(df, column='Sensor Temp (°C)', window=20):
    # Calculate SMA
    sma = df[column].rolling(window=window).mean()

    # Calculate Standard Deviation
    rstd = df[column].rolling(window=window).std()

    # Calculate Upper and Lower Bollinger Bands
    upper_band = sma + 2 * rstd
    lower_band = sma - 2 * rstd

    return upper_band, lower_band


# Add Bollinger Bands to the DataFrame
df['Upper Bollinger Band'], df['Lower Bollinger Band'] = calculate_bollinger_bands(
    df)


# Initialize the Dash app
app = dash.Dash(__name__)

styles = {
    'header': {
        'textAlign': 'center',
        'color': '#0074D9',
        'font-family': 'arial'
    },
    'text_block': {
        'textAlign': 'justify',
        'font-family': 'arial',
        'padding': '10px',
        'margin': '20px',
        'font-weight': 'bold'
    },
    'graph': {
        'padding': '20px',
        'font-family': 'arial'
    }
}

# App layout
app.layout = html.Div(children=[
    html.H1(children='Project Description', style=styles['header']),

    html.Div(children='''
        This application has been created to visualise the data which is being collected from my Raspberry Pi.
        The data being recorded is from both indoor sensors (Temperature and Humidity Sensor) and API data retreived from ...
        The aim of this applciation is to firstly visualise the data but identify areas in which temperature and/or humidty can be altered within
        the house for a more comfortable experience.
    ''', style=styles['text_block']),

    # Add Plotly graphs
    dcc.Graph(id='temp-comparison-graph'),
    dcc.Graph(id='ideal-temp-range-graph'),
    html.Div(id='temp-percentage', style=styles['text_block']),
    dcc.Graph(id='humidity-comparison-graph'),
    dcc.Graph(id='ideal-humidity-range-graph'),
    html.Div(id='humidity-percentage', style=styles['text_block']),
    dcc.Graph(id='combined-ideal-conditions-graph'),
    html.Div(id='ideal-percentage', style=styles['text_block']),
    dcc.Graph(id='correlation-analysis-graph'),
    html.Div(children='''
        From the plot shown above we can see that during the intial period of recording the data, 
        there is a vast amount of time outside of the ideal range for ideal indoor conditions. 
        With more than half the time outside of the ideal ranges, we are presented with an opportunity to 
        create meaningful actuations that will help improve the conditions. From observation, we can see that the main 
        area for improvement is the temperature. The humidity is less of an issue, but we can see it spike above the ideal range when 
        food is being cooked in the kitchen. 
    ''', style=styles['text_block']),
    html.Div(children='''
        From the correlogram we can see there is some correlation between some of the data collectd. In particular, the API Temperature
        and Sensor Humidity surprisingly have the highest correlation. Using some of the correlations, we will see if we can apply future 
        predictions from the API aswell as previous recordings of data to create a model that can predict and give actuations to improve
        the indoor conditions.
    ''', style=styles['text_block']),
    dcc.Graph(id='bollinger-band-graph-temp'),
    dcc.Interval(
        id='interval-component',
        interval=900*1000,  # in milliseconds
        n_intervals=0
    )
])


@app.callback(
    Output('temp-comparison-graph', 'figure'),
    Output('ideal-temp-range-graph', 'figure'),
    Output('temp-percentage', 'children'),
    Output('humidity-comparison-graph', 'figure'),
    Output('ideal-humidity-range-graph', 'figure'),
    Output('humidity-percentage', 'children'),
    Output('combined-ideal-conditions-graph', 'figure'),
    Output('ideal-percentage', 'children'),
    Output('correlation-analysis-graph', 'figure'),
    Output('bollinger-band-graph-temp', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Plot for Temperature Comparison including Heat Index
    fig_temp = px.line(df, x='Time',
                       y=['Sensor Temp (°C)', 'API Temp (°C)'],
                       title='Indoor and Outdoor Temperature Comparison Over Time')

    # New Plot for Ideal Temperature Range
    fig_ideal_temp = px.line(df, x='Time', y=[
                             'Sensor Temp (°C)', 'SMA', 'EMA'], title='Sensor Temperature Comparison to Ideal Range')
    fig_ideal_temp.add_hrect(y0=18, y1=21, line_width=0, fillcolor="green", opacity=0.2,
                             annotation_text="Ideal Temp Range (18-21°C)", annotation_position="top right")

    temp_percentage_text = f"Time in Ideal Temperature Range: {temp_percentage:.2f}%"

    # Plot for Humidity Comparison
    fig_humidity = px.line(df, x='Time', y=['Sensor Humidity (%)', 'API Humidity (%)'],
                           title='Humidity Comparison Over Time')

    fig_ideal_humidity = px.line(df, x='Time', y=['Sensor Humidity (%)'],
                                 title='Sensor Humidity Comparison to Ideal Range')
    fig_ideal_humidity.add_hrect(y0=40, y1=60, line_width=0, fillcolor="green", opacity=0.2,
                                 annotation_text="Ideal Humidity Range (40-60%)", annotation_position="top right")

    humidity_percentage_text = f"Time in Ideal Humidity Range: {humidity_percentage:.2f}%"

    # Scatter Plot for Combined Ideal Temperature and Humidity
    fig_combined_ideal = px.scatter(df, x='Time', y='Ideal Temp & Humidity',
                                    title='Combined Ideal Temperature and Humidity Conditions Over Time',
                                    color='Ideal Temp & Humidity',
                                    color_continuous_scale=['red', 'yellow', 'green'])
    # Update y-axis to show only binary values
    fig_combined_ideal.update_layout(coloraxis_showscale=False)
    fig_combined_ideal.update_yaxes(
        tickvals=[0, 1], ticktext=['Not Ideal', 'Ideal'])

    ideal_percentage_text = f"Time in Ideal Indoor Conditions: {ideal_percentage:.2f}%"

    # Correlation Analysis including Heat Index
    corr_df = df[['Sensor Temp (°C)', 'API Temp (°C)',
                  'Sensor Humidity (%)', 'API Humidity (%)']].corr()
    fig_corr = px.imshow(corr_df, text_auto=True, title="Correlation Analysis")

    boll_fig = px.line(df, x='Time', y='Sensor Temp (°C)',
                       title='Temperature with Bollinger Bands')

    # Add Bollinger Bands
    boll_fig.add_scatter(x=df['Time'], y=df['Upper Bollinger Band'],
                         fill=None, mode='lines', line_color='grey', name='Upper Band')
    boll_fig.add_scatter(x=df['Time'], y=df['Lower Bollinger Band'],
                         fill='tonexty', mode='lines', line_color='grey', name='Lower Band')
    boll_fig.add_hrect(y0=18, y1=21, line_width=0, fillcolor="green", opacity=0.2,
                       annotation_text="Ideal Temp Range (18-21°C)", annotation_position="top right")

    return fig_temp, fig_ideal_temp, temp_percentage_text, fig_humidity, fig_ideal_humidity, humidity_percentage_text, fig_combined_ideal, ideal_percentage_text, fig_corr, boll_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
