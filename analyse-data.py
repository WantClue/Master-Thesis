import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data from CSV files
asic_voltage_df = pd.read_csv('asicVoltage.csv')
frequency_df = pd.read_csv('Freq.csv')
hashrate_df = pd.read_csv('hashRate.csv')
power_df = pd.read_csv('power.csv')
temp_df = pd.read_csv('temp.csv')

# Merge the data on common columns with suffixes to handle duplicates
merged_df = asic_voltage_df.merge(frequency_df, on=['_time', 'host', 'id', 'model'], suffixes=('_asic_voltage', '_frequency'))
merged_df = merged_df.merge(hashrate_df, on=['_time', 'host', 'id', 'model'], suffixes=('', '_hashrate'))
merged_df = merged_df.merge(power_df, on=['_time', 'host', 'id', 'model'], suffixes=('', '_power'))
merged_df = merged_df.merge(temp_df, on=['_time', 'host', 'id', 'model'], suffixes=('', '_temp'))

# Drop duplicate columns resulting from merge
merged_df = merged_df.loc[:,~merged_df.columns.duplicated()]

# Filter out devices with power consumption less than 8W
filtered_df = merged_df[merged_df['power'] >= 8]

# Calculate efficiency (hashrate per watt)
filtered_df['efficiency'] = filtered_df['hashRate'] / filtered_df['power']

# Group by device_id to compute statistics
grouped = filtered_df.groupby('id').agg({
    'hashRate': ['mean', 'median', 'std'],
    'power': ['mean', 'median', 'std'],
    'asicVoltage': ['mean', 'median', 'std'],
    'Freq': ['mean', 'median', 'std'],
    'temp': ['mean', 'median', 'std'],
    'efficiency': ['mean', 'median', 'std']
})

# Identify the device with the highest average efficiency
best_device = grouped['efficiency']['mean'].idxmax()
best_device_data = filtered_df[filtered_df['id'] == best_device]

# Print the best device's details
print(f"Best device ID: {best_device}")
print(grouped.loc[best_device])

# Generate graphs
plt.figure(figsize=(12, 8))

# Hashrate
plt.subplot(2, 3, 1)
plt.hist(filtered_df['hashRate'], bins=20, alpha=0.7)
mean_hashrate = filtered_df['hashRate'].mean()
plt.axvline(filtered_df['hashRate'].mean(), color='k', linestyle='dashed', linewidth=1)
plt.text(mean_hashrate, plt.ylim()[1]*0.9, f'Mean: {mean_hashrate:.2f}', color='k', ha='center')
plt.title('Hashrate Distribution')
plt.xlabel('Hashrate (GH/s)')
plt.ylabel('Frequency')

# Power Consumption
plt.subplot(2, 3, 2)
plt.hist(filtered_df['power'], bins=20, alpha=0.7)
mean_power = filtered_df['power'].mean()
plt.axvline(filtered_df['power'].mean(), color='k', linestyle='dashed', linewidth=1)
plt.text(mean_power, plt.ylim()[1]*0.9, f'Mean: {mean_power:.2f}', color='k', ha='center')
plt.title('Power Consumption Distribution')
plt.xlabel('Power Consumption (W)')
plt.ylabel('Frequency')

# Efficiency
plt.subplot(2, 3, 3)
plt.hist(filtered_df['efficiency'], bins=20, alpha=0.7)
mean_efficiency = filtered_df['efficiency'].mean()
plt.axvline(filtered_df['efficiency'].mean(), color='k', linestyle='dashed', linewidth=1)
plt.text(mean_efficiency, plt.ylim()[1]*0.9, f'Mean: {mean_efficiency:.2f}', color='k', ha='center')
plt.title('Efficiency Distribution')
plt.xlabel('Efficiency (GH/W)')
plt.ylabel('Frequency')

# Temperature
plt.subplot(2, 3, 4)
plt.hist(filtered_df['temp'], bins=20, alpha=0.7)
mean_temp = filtered_df['temp'].mean()
plt.axvline(filtered_df['temp'].mean(), color='k', linestyle='dashed', linewidth=1)
plt.text(mean_temp, plt.ylim()[1]*0.9, f'Mean: {mean_temp:.2f}', color='k', ha='center')
plt.title('Temperature Distribution')
plt.xlabel('Temperature (°C)')
plt.ylabel('Frequency')

# Frequency
plt.subplot(2, 3, 5)
plt.hist(filtered_df['Freq'], bins=20, alpha=0.7)
mean_freq = filtered_df['Freq'].mean()
plt.axvline(filtered_df['Freq'].mean(), color='k', linestyle='dashed', linewidth=1)
plt.text(mean_freq, plt.ylim()[1]*0.9, f'Mean: {mean_freq:.2f}', color='k', ha='center')
plt.title('Frequency Distribution')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()