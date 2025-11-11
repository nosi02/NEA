# ----------------------------------------------------------------------------------------
# OOP forcasting model - weighted moving average
#-----------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
from datetime import datetime, date
class Forecaster: #manage sales data for single product group
    def __init__(self, group_name ,grp_sales_data):
        self.sales_list = grp_sales_data
        self.name = group_name

    def generate_weight(self, ws):
        # creating weights list for window
        weight_list = list(range(1, ws + 1))
        return weight_list

    def calculate_wma(self, window_size, data_to_use=None):
        # make more flexible so can use in predicting future
        if data_to_use is None:
            data_to_use = self.sales_list
        # getting just the last 5 days of data
        data_list = data_to_use[-window_size:]
        forecast = 0
        # in case there is fewer than 5 data items
        if len(data_list) != window_size:
            window_size = len(data_list)
        if window_size == 0:  #check for an empty list
            return None
        weight = self.generate_weight(window_size)
        weighted_sum =  sum(weight)
        # calculating the forecasted value
        for i in range(window_size):
            forecast = forecast + (data_list[i][1] * weight[i])
        forecast = forecast / weighted_sum
        return forecast
    def generate_all_forecasts(self, window_size, weights = None):
        forward = []
        # allowing for custom weights
        if weights is None:
            weights = self.generate_weight(window_size)
        if len(weights) != window_size:
            print(f" There needs to be a total of {window_size} weights")
            return []
        weighted_sum = sum(weights)
        for i in range(window_size, len(self.sales_list)):
            # creating the window
            elements = self.sales_list[i-window_size:i]
            forecast = 0
            # calculating the forecasted value
            for j in range(window_size):
                forecast = forecast + (elements[j][1] * weights[j])
            forecast = forecast / weighted_sum
            forecast_date = self.sales_list[i][0]
            forward.append([forecast_date, forecast])
        return forward
    def plot_forecast(self, window_size, forward):
        dates = []
        quantity = []
        forecast_qty = []
        for item in self.sales_list:
            dates.append(datetime.strptime(item[0], '%d/%m/%y'))
            quantity.append(item[1])
        for i in forward:
            forecast_qty.append(i[1])
        forecast_dates = dates[window_size:]
        real_qty = quantity[window_size:]
        #line graph for predicted sales
        plt.plot(forecast_dates, real_qty,label='Actual Sales' )
        #line graph for real sales
        plt.plot(forecast_dates, forecast_qty,label='Forecasted Sales')
        plt.xlabel("Date")  # Label for the X-axis
        plt.ylabel("Quantity Sold")  # Label for the Y-axis
        plt.title(f"Line graph of predicted sales vs real sales data for {self.name} in a {window_size} window")# Chart title
        plt.legend()
        plt.gcf().autofmt_xdate()
        plt.show()
    def predict_future_sequence(self, num_days, window_size):
        temp_list = self.sales_list[-window_size:]
        future_forecasts = []
        for i in range(int(num_days)):
            next_value = self.calculate_wma(window_size, data_to_use=temp_list)
            if next_value is None:
                break
            future_forecasts.append(next_value)
            temp_list.pop(0)
            temp_list.append(["Future Day", next_value])
        return future_forecasts


