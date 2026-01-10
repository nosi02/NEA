from Forecaster import Forecaster
from datetime import datetime, timedelta

class MRP:
    def __init__(self, lead_time: object, forecasts: object, inventory: object, safety_stocks: object, period: object, sales_mix: object, product_costs ) -> object:
        self.inventory = inventory
        self.lead_times = lead_time
        self.safety_stock = safety_stocks
        self.forecast_sales = forecasts
        self.period_length = period
        self.sales_mix = sales_mix
        self.product_costs = product_costs
    def order_plan(self):
        planned_orders = []
        today = datetime.now()
        for grp_name, daily_forecasts in self.forecast_sales.items():
            # get specific details for each product group
            projected_inventory = self.inventory.get(grp_name, 0)
            lead_time = self.lead_times.get(grp_name, 2)#added default fallback
            safety_stock = self.safety_stock.get(grp_name, 2)
            period_time = self.period_length
            cooldown = -1 # no new orders until after this day
            # predict inventory day by day
            #enumerate makes it a tuple so can loop through it
            for day_index, demand in enumerate(daily_forecasts):
                projected_inventory -= demand
                if projected_inventory <= safety_stock and day_index >= cooldown:
                    deficit = safety_stock - projected_inventory
                    future_demand_slice = daily_forecasts[day_index: day_index + lead_time + period_time]
                    demand_during_lead_time = sum(future_demand_slice)
                    quantity_to_order = deficit + demand_during_lead_time

                    # Avoid placing tiny orders
                    if quantity_to_order <= 0:
                        continue

                    # figure out when order must be placed
                    days_until_order = max(0, day_index - lead_time)
                    order_placement_date = today + timedelta(days=days_until_order)
                    expected_arrival_date = today + timedelta(days=day_index)

                    #create order list
                    product_mix = self.sales_mix[grp_name]
                    for product_name, percentage in product_mix.items():
                        individual_quantity = round(quantity_to_order * percentage)
                        cost_info = self.product_costs.get(product_name, {'supplier': 'Unknown', 'cost': 0})
                        unit_cost = cost_info.get('cost', 0.0)
                        supplier_name = cost_info.get('supplier', 'Unknown')
                        total_estimated_cost = individual_quantity * unit_cost
                        if individual_quantity <= 0: # Avoid placing tiny orders
                            continue
                        individual_order_list = {
                            'Product': product_name,
                            'QuantityToOrder': individual_quantity,
                            'ProductGroup': grp_name,
                            'Supplier': supplier_name,
                            'UnitCost': unit_cost,
                            'TotalCost': total_estimated_cost,
                            'OrderPlacementDate': order_placement_date.strftime('%Y-%m-%d'),
                            'ExpectedArrivalDate': expected_arrival_date.strftime('%Y-%m-%d')
                         }
                        planned_orders.append(individual_order_list)

                    projected_inventory += quantity_to_order # inventory increase due to planned order
                    cooldown = day_index + self.period_length #not place another order until after period time over
        return planned_orders

