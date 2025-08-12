test_data = [['01/05/25', 1], ['02/05/25', 2], ['08/05/25', 2], ['15/05/25', 2], ['27/05/25', 4], ['30/05/25', 12], ['02/06/25', 8], ['03/06/25', 4], ['04/06/25', 8]]
weights = [1,2,3,4,5,6,7,8,9,10]
weighted_sum =  sum(weights)
forecast = 0
for i in range(len(weights) -1) :
    forecast = forecast + (test_data[i][1] * weights[i])
forecast = forecast / weighted_sum
print(forecast)
real = ['11/06/25', 4]