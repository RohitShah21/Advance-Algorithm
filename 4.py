def load_balancing():
    # 1. Model Input Data [cite: 598]
    demand_table = {
        "06": {"A": 20, "B": 15, "C": 25}, # Total 60
        "07": {"A": 22, "B": 16, "C": 28}  # Total 66
    }
    
    sources = [
        {"id": "S1", "type": "Solar", "cap": 50, "hours": range(6, 19), "cost": 1.0},
        {"id": "S2", "type": "Hydro", "cap": 40, "hours": range(0, 24), "cost": 1.5},
        {"id": "S3", "type": "Diesel", "cap": 60, "hours": range(17, 24), "cost": 3.0}
    ]
    
    print(f"{'Hour':<5} {'District':<10} {'Solar':<8} {'Hydro':<8} {'Diesel':<8} {'Total':<8} {'Demand':<8} {'% Met':<8}")
    print("-" * 80)
    
    total_cost = 0
    total_renewable = 0
    total_energy = 0
    
    for hour_str, districts in demand_table.items():
        hour = int(hour_str)
        
        # 2. Greedy Source Prioritization [cite: 602]
        # Filter available sources and sort by cost
        available_sources = sorted(
            [s for s in sources if hour in s['hours']], 
            key=lambda x: x['cost']
        )
        
        # Sum demands
        hour_demand = sum(districts.values())
        remaining_demand = hour_demand
        
        usage = {"Solar": 0, "Hydro": 0, "Diesel": 0}
        
        # Allocate
        for src in available_sources:
            take = min(src['cap'], remaining_demand)
            usage[src['type']] += take
            remaining_demand -= take
            
            cost = take * src['cost']
            total_cost += cost
            total_energy += take
            if src['type'] in ["Solar", "Hydro"]:
                total_renewable += take
                
        # Output results [cite: 607]
        total_used = sum(usage.values())
        pct_met = (total_used / hour_demand) * 100
        
        # Per district output logic would go here, simplified for summary
        for dist, req in districts.items():
             # In a real balancing algo, we'd track exactly which source went where.
             # This assumes pooled resources.
             print(f"{hour_str:<5} {dist:<10} {'-':<8} {'-':<8} {'-':<8} {'-':<8} {req:<8} {'-':<8}")

        print(f"{'Agg':<5} {'ALL':<10} {usage['Solar']:<8} {usage['Hydro']:<8} {usage['Diesel']:<8} {total_used:<8} {hour_demand:<8} {pct_met:.1f}%")

    print("-" * 80)
    print(f"Total Cost: Rs. {total_cost}")
    print(f"Renewable Energy: {(total_renewable/total_energy)*100:.1f}%")

if __name__ == "__main__":
    load_balancing()