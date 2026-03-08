import os
import json
import pandas as pd
import plotly
import plotly.express as px
from jinja2 import Environment, FileSystemLoader

# --- Data Loading and Cleaning ---
def load_data():
    ev_india = pd.read_csv("data/EVIndia.csv")
    ev_models = pd.read_csv("data/ElectricCarData_Clean.csv")
    charging_stations = pd.read_csv("data/electric_vehicle_charging_station_list.csv")
    cheap_cars = pd.read_csv("data/Cheapestelectriccars-EVDatabase.csv")

    for df in [ev_india, ev_models, charging_stations, cheap_cars]:
        df.columns = df.columns.str.strip()
        
    return ev_india, ev_models, charging_stations, cheap_cars

# --- Graph Generation ---
def get_charging_graphs(stations):
    graphs = {}
    if not stations.empty:
        v_stations = stations.dropna(subset=['region'])
        
        # 1. Charging stations by city/region
        region_counts = v_stations['region'].value_counts().reset_index()
        region_counts.columns = ['region', 'count']
        fig1 = px.bar(region_counts.head(15), x='region', y='count', 
                     title="Top 15 Regions by Charging Stations",
                     labels={'region': 'Region/City', 'count': 'Number of Stations'})
        graphs['stations_by_city'] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        
        # 2. Charging heatmap
        fig2 = px.density_mapbox(v_stations, lat='latitude', lon='longitude', zoom=3,
                                 mapbox_style="carto-positron",
                                 title="Charging Station Heatmap")
        graphs['charging_heatmap'] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

        # 3. Charging power distribution
        fig3 = px.histogram(stations, x='power',
                            title="Charging Power Distribution",
                            labels={'power': 'Power Rating'})
        power_counts = stations['power'].value_counts().nlargest(10).index
        fig3.update_xaxes(categoryorder='array', categoryarray=power_counts)
        graphs['power_distribution'] = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    return graphs

def get_battery_graphs(ev_models):
    graphs = {}
    if not ev_models.empty:
        ev_models['Range_Km'] = pd.to_numeric(ev_models['Range_Km'], errors='coerce')
        ev_models['Efficiency_WhKm'] = pd.to_numeric(ev_models['Efficiency_WhKm'], errors='coerce')
        ev_models['PriceEuro'] = pd.to_numeric(ev_models['PriceEuro'], errors='coerce')
        
        ev_models = ev_models.dropna(subset=['Range_Km', 'Efficiency_WhKm', 'PriceEuro'])
        ev_models['Full_Name'] = ev_models['Brand'] + " " + ev_models['Model']

        # Efficiency vs Range
        fig1 = px.scatter(ev_models, x='Efficiency_WhKm', y='Range_Km', color='Brand',
                          hover_name='Full_Name',
                          title="Efficiency vs Range",
                          labels={'Efficiency_WhKm': 'Efficiency (Wh/Km)', 'Range_Km': 'Range (Km)'})
        graphs['efficiency_vs_range'] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        # Efficiency vs Cost
        fig2 = px.scatter(ev_models, x='Efficiency_WhKm', y='PriceEuro', color='Brand',
                          hover_name='Full_Name',
                          title="Efficiency vs Price (€)",
                          labels={'Efficiency_WhKm': 'Efficiency (Wh/Km)', 'PriceEuro': 'Price (€)'})
        graphs['efficiency_vs_cost'] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        
    return graphs

def get_model_comparison_graphs(cheap):
    graphs = {}
    if not cheap.empty:
        cheap['Range_Num'] = cheap['Range'].str.replace(' km', '').astype(float)
        cheap['Efficiency_Num'] = cheap['Efficiency'].str.replace(' Wh/km', '').astype(float)
        
        cheap['Price_Num'] = cheap['PriceinGermany'].str.replace('€', '').str.replace(',', '').str.replace('N/A', '0')
        cheap['Price_Num'] = pd.to_numeric(cheap['Price_Num'], errors='coerce')
        
        valid_cheap = cheap[cheap['Price_Num'] > 0].sort_values('Price_Num').head(20) 
        
        fig1 = px.bar(valid_cheap, x='Name', y='Price_Num', color='Name',
                      title="Price Comparison (Top 20 Cheapest EVs in Germany)",
                      labels={'Price_Num': 'Price (€)', 'Name': 'EV Model'})
        graphs['price_comp'] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        
        fig2 = px.bar(valid_cheap, x='Name', y='Range_Num', color='Name',
                      title="Range Comparison",
                      labels={'Range_Num': 'Range (km)', 'Name': 'EV Model'})
        graphs['range_comp'] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        
        fig3 = px.bar(valid_cheap, x='Name', y='Efficiency_Num', color='Name',
                      title="Efficiency Comparison",
                      labels={'Efficiency_Num': 'Efficiency (Wh/km)', 'Name': 'EV Model'})
        graphs['eff_comp'] = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    return graphs

# --- Main Build Process ---
def build_site():
    print("Loading data...")
    ev_india, ev_models, charging_stations, cheap_cars = load_data()
    
    print("Calculating stats...")
    stats = {
        'total_indian_evs': len(ev_india),
        'total_global_models': len(ev_models),
        'total_charging_stations': len(charging_stations),
        'cheapest_evs_listed': len(cheap_cars)
    }
    
    print("Generating graphs...")
    charging_graphs = get_charging_graphs(charging_stations)
    battery_graphs = get_battery_graphs(ev_models)
    model_graphs = get_model_comparison_graphs(cheap_cars)

    print("Rendering templates...")
    env = Environment(loader=FileSystemLoader('src/templates'))
    
    # Render Index
    template = env.get_template('index.html')
    output_from_parsed_template = template.render(stats=stats)
    with open("index.html", "w", encoding='utf-8') as fh:
        fh.write(output_from_parsed_template)

    # Render Charging
    template = env.get_template('charging.html')
    output_from_parsed_template = template.render(graphs=charging_graphs)
    with open("charging.html", "w", encoding='utf-8') as fh:
        fh.write(output_from_parsed_template)
        
    # Render Battery
    template = env.get_template('battery.html')
    output_from_parsed_template = template.render(graphs=battery_graphs)
    with open("battery.html", "w", encoding='utf-8') as fh:
        fh.write(output_from_parsed_template)
        
    # Render Models
    template = env.get_template('models.html')
    output_from_parsed_template = template.render(graphs=model_graphs)
    with open("models.html", "w", encoding='utf-8') as fh:
        fh.write(output_from_parsed_template)

    print("Site built successfully! Open index.html to view.")

if __name__ == "__main__":
    build_site()
