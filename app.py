from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_plotly
import plotly.graph_objects as go
from src.simulation_engine import calculate_deterministic_metrics, run_monte_carlo_simulation
#automation bridge
import requests
import yaml

DATA_URL = "https://raw.githubusercontent.com/shaurya-portfolio/Ai-FinOps-Simulator/main/src/cloud_pricing.yaml"

finops_data = {
    "market_size": 100000,
    "market_share": 5.0,
    "unit_price": 150.0,       
    "fixed_costs": 50000,
    "variable_cost": 60.0      
}

try:
    response = requests.get(DATA_URL)
    if response.status_code == 200:
        live_data = yaml.safe_load(response.text)
        
        
        aws_a100_on_demand = live_data['providers']['aws']['nvidia_a100']['on_demand_rate']
        aws_a100_spot = live_data['providers']['aws']['nvidia_a100']['spot_rate_baseline']
        
       
        finops_data["unit_price"] = aws_a100_on_demand
        finops_data["variable_cost"] = aws_a100_spot
        
except Exception as e:
    print(f"Error in Live Data Lane: {e}")


#Frontend UI
app_ui = ui.page_fluid(
    #CSS Injection
    ui.tags.head(
        ui.tags.style("""
            /* Main background aur font */
            body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, sans-serif; }
            
            /* Main Header styling */
            h2 { color: #1e3a8a; font-weight: 700; padding-top: 15px; padding-bottom: 5px; }
            
            /* Sidebar ko premium dark look dena */
            .bslib-sidebar-layout > .bslib-sidebar { 
                background-color: #1e293b !important; 
                color: #f8fafc !important; 
                border-right: 1px solid #cbd5e1;
            }
            
            /* Sidebar ke headings aur text ka color */
            .bslib-sidebar h4 { color: #38bdf8 !important; font-weight: 600; }
            .bslib-sidebar label { color: #e2e8f0 !important; font-weight: 500; }
            
            /* Main Tabs ki styling */
            .nav-underline .nav-link.active { color: #0284c7 !important; border-bottom-color: #0284c7 !important; font-weight: bold; }
            .nav-underline .nav-link { color: #64748b; font-weight: 500; }
        """)
    ),

    ui.h2("AI FinOps And Cloud CapEx Simulator"),
    ui.hr(style="border-top: 2px solid #cbd5e1;"),
    ui.layout_sidebar(
        #sidebar
        ui.sidebar(
            ui.h4("FinOps Parameters"),
            ui.hr(style="border-top: 1px solid #475569;"),

            
            ui.input_numeric("market_size","Total AI Compute Demand (Hours)", value=finops_data.get("market_size", 100000)),
            ui.input_slider("market_share","FinOps Agent Adoption Rate (%)", min=0.0, max=100.0, value=finops_data.get("market_share", 5.0), step=0.5),
            ui.input_numeric("unit_price", "On-Demand GPU Hourly Rate ($)", value=finops_data.get("unit_price", 150)),
            ui.input_numeric("fixed_costs", "Base CapEx ($)", value=finops_data.get("fixed_costs", 50000)),
            ui.input_numeric("variable_cost", "Optimized GPU Spot Rate ($)", value=finops_data.get("variable_cost", 60)),
            width="320px"
        ),

        ui.navset_card_underline(
            #Market Sizing
            ui.nav_panel(
                "Market Sizing",
                ui.h4("Deterministic Business Model", style="color: #334155; margin-top: 15px;"),
                output_widget("deterministic_chart")
            ),

            #ROI Risk Simulaton
            ui.nav_panel(
                "ROI Risk Simulation",
                ui.h4("Monte Carlo Risk Analysis", style="color: #334155; margin-top: 15px;"),
                output_widget("monte_carlo_chart")
            )
        )
    )
)

#Backend Server

def server(input, output, session):
    
    #REACTIVE CALCULATOR
    
    @reactive.calc
    def run_deterministic_model():
        
        return calculate_deterministic_metrics(
            market_size=input.market_size() or 0,
            market_share_pct=input.market_share() or 0,
            unit_price=input.unit_price() or 0,
            fixed_costs=input.fixed_costs() or 0,
            variable_cost_per_unit=input.variable_cost() or 0
        )

    #VISUAL RENDERING
    @output
    @render_plotly
    def deterministic_chart():
        
        data = run_deterministic_model()
        
        # Plotly Waterfall chart
        fig = go.Figure(go.Waterfall(
            name="FinOps Breakdown",
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Compute Revenue", "Cloud Infra Costs", "Net Margins"], # Labels updated
            textposition="outside",
            text=[f"${data['projected_revenue']:,.0f}", f"-${data['total_costs']:,.0f}", f"${data['net_profit']:,.0f}"],
            y=[data['projected_revenue'], -data['total_costs'], data['net_profit']],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}}, 
            totals={"marker": {"color": "#3b82f6"}}      
        ))
        

        fig.update_layout(title="FinOps Unit Economics: Revenue vs Cloud Costs", showlegend=False, margin=dict(t=50, l=20, r=20, b=20))
        return fig

    @reactive.calc
    def run_risk_model():
        return run_monte_carlo_simulation(
            market_size=input.market_size() or 0,
            base_market_share_pct=input.market_share() or 0,
            base_unit_price=input.unit_price() or 0,
            fixed_costs=input.fixed_costs() or 0,
            variable_cost_per_unit=input.variable_cost() or 0
        )
    
    @output
    @render_plotly
    def monte_carlo_chart():
        risk_data = run_risk_model()
        
        fig = go.Figure(data=[
            go.Bar(name='Worst Case (10%)', x=['Worst Case'], y=[risk_data['worst_case_profit']], marker_color='#ef4444'),
            go.Bar(name='Expected (50%)', x=['Expected'], y=[risk_data['expected_profit']], marker_color='#f59e0b'),
            go.Bar(name='Best Case (90%)', x=['Best Case'], y=[risk_data['best_case_profit']], marker_color='#10b981')
        ])
        
        # Chart aesthetics
        fig.update_layout(
            title="Profitability Risk Scenarios (10k Iterations)",
            yaxis_title="Net Profit ($)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, l=20, r=20, b=20)
        )
        return fig

app = App(app_ui, server)