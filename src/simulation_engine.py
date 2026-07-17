import numpy as np


def calculate_deterministic_metrics(market_size, market_share_pct, unit_price, fixed_costs, variable_cost_per_unit):
    """
    Calculates baseline business metrics using deterministic (fixed) inputs.
    
    Args:
        market_size (float/int): Total addressable market volume.
        market_share_pct (float): Target market share percentage (0-100).
        unit_price (float): Selling price per unit.
        fixed_costs (float): Total fixed operational costs.
        variable_cost_per_unit (float): Variable cost incurred per unit.
        
    Returns:
        dict: A dictionary containing TAM revenue, projected revenue, 
              total costs, net profit, and ROI percentage.
    """

    #TAM 
    tam_revenue = market_size * unit_price

    #Target Volume
    target_volume = market_size * (market_share_pct / 100)

    #Projected Revenue
    projected_revenue = target_volume * unit_price

    #Total Cost = Fixed Cost + Variable Cost
    total_costs = fixed_costs + (target_volume * variable_cost_per_unit)

    #Net Profit
    net_profit = projected_revenue - total_costs

    #ROI Percentage
    if total_costs > 0:
        roi_pct = (net_profit / total_costs) * 100 
    else:
        roi_pct = 0.0
    
    return {
        "tam_revenue": round(tam_revenue, 2),
        "projected_revenue": round(projected_revenue, 2),
        "total_costs": round(total_costs, 2),
        "net_profit": round(net_profit, 2),
        "roi_percentage": round(roi_pct, 2)
    }

def run_monte_carlo_simulation(market_size, base_market_share_pct, base_unit_price, fixed_costs, variable_cost_per_unit, iterations=10000):
    """
    Executes a vectorized Monte Carlo simulation to forecast risk and volatility,
    optimized via numpy to prevent client-side browser UI freezing.
    
    Args:
        market_size (float/int): Base market volume.
        base_market_share_pct (float): Base market share percentage estimate.
        base_unit_price (float): Base selling price per unit.
        fixed_costs (float): Fixed operational costs.
        variable_cost_per_unit (float): Variable cost per unit.
        iterations (int): Number of simulated scenarios (default 10,000).
        
    Returns:
        dict: Statistical percentiles (10th worst-case, 50th expected, 90th best-case) 
              for Net Profit and ROI.
    """

    #Simulation Volatility
    simulated_market_share = np.random.normal(loc=base_market_share_pct,scale=(base_market_share_pct*0.1),size=iterations)
    simulated_unit_price = np.random.normal(loc=base_unit_price,scale=(base_unit_price*0.05),size = iterations )

    # as market share cant be negative
    simulated_market_share = np.maximum(simulated_market_share,0)

    #Vectorizd Math
    sim_target_volume = market_size * (simulated_market_share/100)
    sim_revenue = sim_target_volume * simulated_unit_price
    sim_costs = fixed_costs + (sim_target_volume * variable_cost_per_unit)

    sim_net_profit = sim_revenue - sim_costs

    #ROI Calculation
    sim_roi_pct = np.where(sim_costs>0,(sim_net_profit/sim_costs)*100,0)

    #Extracting Percentiles
    return {
        "worst_case_roi": round(float(np.percentile(sim_roi_pct, 10)), 2),   # 10% probability
        "expected_roi": round(float(np.percentile(sim_roi_pct, 50)), 2),     # 50% probability
        "best_case_roi": round(float(np.percentile(sim_roi_pct, 90)), 2),    # 90% probability
        "worst_case_profit": round(float(np.percentile(sim_net_profit, 10)), 2),
        "expected_profit": round(float(np.percentile(sim_net_profit, 50)), 2),
        "best_case_profit": round(float(np.percentile(sim_net_profit, 90)), 2)
    }



if __name__ == "__main__":
    # Deterministic test
    det_results = calculate_deterministic_metrics(100000, 5.0, 150, 50000, 60)
    print("\n[1] Deterministic Math Test Results:", det_results)
    
    # Monte Carlo test (10,000 iterations)
    mc_results = run_monte_carlo_simulation(100000, 5.0, 150, 50000, 60)
    print("\n[2] Monte Carlo Risk Engine (10k Iterations):", mc_results)