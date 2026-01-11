import pandas as pd
import plotly.graph_objects as go
import time
from plotly.subplots import make_subplots
from flask import Flask, render_template, make_response, request

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/api')
def createpage():

  query = request.args.get('corner')
  corner = 'corner'+str(query)
  # Step 1: Read the CSV file
  data = pd.read_csv(f'/app/data/{corner}_data.csv')
 # print(f'Data is: {data}')
  # Cleaning and converting the data
  data['totalGenerated'] = data['totalGenerated'].str.strip('WH').astype(int)
  data['totalGenerated'] = data['totalGenerated'].diff()
  data['loadPower'] = data['loadPower'].str.strip('W').astype(float)

  # Calculate excess
  data['excess'] = data['totalGenerated'] - data['loadPower']

  # Create the first figure for hourly data
  fig1 = make_subplots(rows=1, cols=1, subplot_titles=('Hourly Data'))

  # Set colors based on value
  excess_colors = ['red' if val < 0 else 'blue' for val in data['excess']]
  loadPower_colors = ['red' if val < 0 else 'orange' for val in data['loadPower']]

  # Adding traces for charging battery and used power
  fig1.add_trace(
       go.Bar(
          x=data['date'],
          y=data['loadPower'],
          name='Used Power',
          marker_color=loadPower_colors
      )
  )
  fig1.add_trace(
      go.Bar(
          x=data['date'],
          y=data['excess'],
          name='Charging Battery',
          marker_color=excess_colors
      )
  )

  # if data['nodeIP'][0] == "10.0.70.90":
  nodeName = f"Corner {query}"
  # Update layout for the first figure
  fig1.update_layout(title_text=nodeName, barmode='stack')

  # Prepare daily data for the second figure
  data['date'] = pd.to_datetime(data['date'])  # Ensure 'date' is in datetime format
  data.set_index('date', inplace=True)

  # Create daily data with resampling
  dailyData = data.resample('D').sum()

  # Daily excess calculation
  dailyData['excess'] = dailyData['totalGenerated'] - dailyData['loadPower']

  # Create the second figure for daily data
  fig2 = make_subplots(rows=1, cols=1, subplot_titles=('Daily Data'))

  # Set colors based on daily values
  daily_excess_colors = ['red' if val < 0 else 'blue' for val in dailyData['excess']]

  # Adding daily charging battery to the second figure
  fig2.add_trace(
    go.Bar(
        x=dailyData.index,
        y=dailyData['excess'],
        name='Daily Charging Battery',
        marker_color=daily_excess_colors
    )
  )

  # Update layout for the second figure
  fig2.update_layout(title_text='Daily Power Data', barmode='stack')

  # Step 3: Create tables for temperature and battery voltage metrics
  min_temp = data['systemTemp'].min()
  max_temp = data['systemTemp'].max()
  min_voltage = data['batteryVoltage'].min()  # Assuming this column exists
  max_voltage = data['batteryVoltage'].max()  # Assuming this column exists
  min_Power = data['sunPower'].min()  # Assuming this column exists
  max_Power = data['sunPower'].max()  # Assuming this column exists

  # Create a table figure for temperature
  temp_table = go.Figure(data=[go.Table(
    header=dict(values=['System Temp', 'Celcius']),
    cells=dict(values=[
        ['Minimum', 'Maximum'],
        [min_temp, max_temp]
    ])
  )])

  # Create a table figure for battery voltages
  voltage_table = go.Figure(data=[go.Table(
    header=dict(values=['Battery Voltage', 'Volts']),
    cells=dict(values=[
        ['Minimum', 'Maximum'],
        [min_voltage, max_voltage]
    ])
  )])

  # Create a table figure for battery voltages
  watt_table = go.Figure(data=[go.Table(
    header=dict(values=['Instant Watts', 'wH']),
    cells=dict(values=[
        ['Minimum', 'Maximum'],
        [min_Power, max_Power]
    ])
  )])
  # Create a table figure for battery voltages
  dead_table = go.Figure(data=[go.Table(
    header=dict(values=['Instant Watts', 'wH']),
    cells=dict(values=[
        ['Minimum', 'Maximum'],
        [min_Power, max_Power]
    ])
  )])
  temp_table.update_layout(width=500, height=250)
  voltage_table.update_layout(width=500, height=250)
  watt_table.update_layout(width=500, height=250)
  dead_table.update_layout(width=500, height=250)


  with open('/app/app/templates/combined_output.html', 'w') as f:
    # Write the opening HTML and head section
    f.write('<html><head><style>')
    f.write('table { border-collapse: collapse; margin: 10px; width: 100%; }')
    f.write('th, td { border: 1px solid black; padding: 8px; text-align: left; }')
    f.write('.container { display: flex; justify-content: left; }')
    f.write('</style></head><body>')
    # Write the figures
    f.write(fig1.to_html(full_html=True, include_plotlyjs='cdn'))
    f.write(fig2.to_html(full_html=False, include_plotlyjs=False))
    # Write the tables in a container for side-by-side display
    f.write('<div class="container">')
    f.write(temp_table.to_html(full_html=False, include_plotlyjs=False, div_id='temp_table'))
    f.write(watt_table.to_html(full_html=False, include_plotlyjs=False))
    f.write(voltage_table.to_html(full_html=False, include_plotlyjs=False))
    f.write(dead_table.to_html(full_html=False, include_plotlyjs=False))
    f.write('</div>')
    # Write the closing HTML tags
    f.write('</body></html>')
    
    # Render the template with dynamic content
    response = make_response(render_template('combined_output.html'))

    # Disable caching by setting headers
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    del(data) 
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8091)
