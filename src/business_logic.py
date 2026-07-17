
def calculate_tam(global_spend_bn,waste_pct,adoption_pct):
    """
    Calculates the Total Addressable Market (TAM) for the Cloud GPU Optimization Agent.
    
    Args:
        global_spend_bn (float): Total global expenditure on AI cloud compute (in Billions USD).
        waste_pct (float): The percentage of cloud spend wasted due to inefficient GPU provisioning (0.0 to 1.0).
        adoption_pct (float): The estimated market penetration or adoption rate of such FinOps agents (0.0 to 1.0).
        
    """
    # TAM = GLOBAL_AI_COMPUTE_SPEND * CAPEX_WASTE_PERCENTAGE * AGENT_ADOPTION_RATE

    #computing total waste which is our real problem statement
    TOTAL_WASTED_SPEND = global_spend_bn * waste_pct

    #market capture
    ADDRESSABLE_MARKET = TOTAL_WASTED_SPEND *adoption_pct

    return round(ADDRESSABLE_MARKET,2)

def calculate_client_roi(total_gpu_hours,on_demand_rate,spot_rate,agent_licensing_fee):
    """
    Calculates the Return on Investment (ROI) and net savings for a specific client 
    using the FinOps agent, comparing on-demand CapEx versus optimized spot CapEx.
    
    Args:
        total_gpu_hours (float): Total compute hours required by the client for AI workloads.
        on_demand_rate (float): Standard hourly rate for an on-demand GPU (e.g., $3.00 for H100).
        spot_rate (float): Fluctuating hourly rate for a spot instance GPU.
        agent_licensing_fee (float): The fixed monthly/yearly fee charged by the FinOps agent software.
        
    Returns:
        dict: A dictionary containing total on-demand cost, optimized cost, and net savings.
        """
     
    # NET_SAVINGS = (TOTAL_GPU_HOURS * ONDEMAND_RATE) - (TOTAL_GPU_HOURS * SPOT_RATE) - AGENT_FEE


    #cost without client
    TOTAL_ONDEMAND_COST = total_gpu_hours * on_demand_rate

    #cost on spot instances after agent usage 
    OPTIMIZED_SPOT_COST =   total_gpu_hours * spot_rate

    #gross savings
    GROSS_SAVINGS = TOTAL_ONDEMAND_COST - OPTIMIZED_SPOT_COST

    #net savings
    NET_SAVINGS = GROSS_SAVINGS - agent_licensing_fee

    return {
        "on_demand_cost": round(TOTAL_ONDEMAND_COST, 2),
        "optimized_cost": round(OPTIMIZED_SPOT_COST, 2),
        "net_savings": round(NET_SAVINGS, 2)
    }
     