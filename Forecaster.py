# ----------------------------------------------------------------------------------------
# OOP forcasting model - weighted moving average
#-----------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, timedelta
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
            try:# Ensure date format matches data (dd/mm/yy)
                dates.append(datetime.strptime(item[0], '%d/%m/%y'))
                quantity.append(item[1])
            except (ValueError, TypeError,IndexError):
                continue
        if not dates:
            print("DEBUG: No dates were parsed. Check your database date format!")
            return Figure()
        for i in forward:
            if isinstance(i, (list, tuple)):
                forecast_qty.append(i[1])
            else:
                forecast_qty.append(i)
        #forecast_dates = dates[window_size:]
        #real_qty = quantity[window_size:]
        #handeling any potential errors
        #min_len = min(len(forecast_dates), len(real_qty), len(forecast_qty))
        #forecast_dates = forecast_dates[:min_len]
        #real_qty = real_qty[:min_len]
        #forecast_qty = forecast_qty[:min_len]
        #Generate future dates
        last_date = dates[-1]
        future_dates = [last_date + timedelta(days=x + 1) for x in range(len(forecast_qty))]
        #line graph for predicted sales
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates, quantity,label='Historical Sales' , linewidth=1.5)
        #line graph for real sales
        combined_forecast_dates = [dates[-1]] + future_dates
        combined_forecast_qty= [quantity[-1]] + forecast_qty
        ax.plot(combined_forecast_dates, combined_forecast_qty,label='Predicted Sales',linestyle='--')
        ax.set_xlabel("Date")  # Label for the X-axis
        ax.set_ylabel("Quantity Sold")  # Label for the Y-axis
        ax.set_title(f"Forecast for {self.name} ({window_size} Day Window)")#Chart title
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()
        return fig
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
    def calculate_accuracy(self,window_size):
        historical_forecasts = self.generate_all_forecasts(window_size)
        actual_sales_data = self.sales_list[window_size:]
        if len(historical_forecasts) == 0:
            return {'MAE': None, 'RMSE': None} # MAE = mean absolute error RMSE = root mean squared error
        total_absolute_error = 0
        total_squared_error = 0
        combined = zip(historical_forecasts,actual_sales_data) #combining into one list to iterate through
        for actual_data, forecast_data in combined:
            actual_qty = actual_data[1]
            forecast_qty = forecast_data[1]
            error = actual_qty - forecast_qty
            total_absolute_error += abs(error)
            total_squared_error += error ** 2
        n = len(historical_forecasts)
        mae = total_absolute_error/n
        rmse = (total_squared_error/n) ** 0.5
        return {'MAE': mae, 'RMSE': rmse}


