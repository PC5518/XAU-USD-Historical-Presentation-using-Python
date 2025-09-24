import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# --- 1. DEFINE KEY HISTORICAL EVENTS ---
events = [
    {'date': '2000-03-10', 'label': 'Dot-com Bubble Bursts', 'y_offset': -0.1}, # Offset as a percentage
    {'date': '2001-09-11', 'label': '9/11 Attacks', 'y_offset': -0.1},
    {'date': '2008-09-15', 'label': 'Financial Crisis', 'y_offset': -0.15},
    {'date': '2008-11-25', 'label': 'QE1 Begins', 'y_offset': -0.1},
    {'date': '2011-08-01', 'label': 'EU Debt Crisis', 'y_offset': -0.15},
    {'date': '2020-03-11', 'label': 'COVID-19 Pandemic', 'y_offset': -0.15},
]
for event in events:
    event['date'] = pd.to_datetime(event['date'])
    event['plotted'] = False

# --- 2. Load and Prepare the Data ---
try:
    df = pd.read_csv('gold_yahoo_gc_f.csv')
except FileNotFoundError:
    print("Error: 'gold_yahoo_gc_f.csv' not found.")
    exit()

df['Date'] = pd.to_datetime(df['Date'].str[:19])
df = df.sort_values('Date').reset_index(drop=True)

starting_price = df['price'].iloc[0]
first_date = df['Date'].iloc[0]

# --- 3. Setup the Plot ---
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(16, 9))

ax.set_title('Gold Price: An Animated History', fontsize=24, pad=20, fontname='Arial', weight='bold',color="#D9FF00")
ax.set_ylabel('Price (USD)', fontsize=16, fontname='Arial')
ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='#555555')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Initialize text elements
date_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=18, fontfamily='monospace', verticalalignment='top')
price_text = ax.text(0.02, 0.88, '', transform=ax.transAxes, fontsize=18, fontfamily='monospace', verticalalignment='top', color="#F6FF00")
return_text = ax.text(0.27, 0.80, '', transform=ax.transAxes, fontsize=19, fontfamily='monospace',
                      verticalalignment='top', horizontalalignment='right', weight='bold')

GREEN = '#2ECC71'
RED = '#E74C3C'

# --- 4. Define the Master Animation Function ---
def update(frame):
    current_date = df['Date'][frame]
    current_price = df['price'][frame]
    
    # Plot the new line segment
    if frame > 0:
        prev_date = df['Date'][frame-1]
        prev_price = df['price'][frame-1]
        color = GREEN if current_price >= prev_price else RED
        ax.plot([prev_date, current_date], [prev_price, current_price], color=color, linewidth=2)

    ### NEW DYNAMIC AXIS LOGIC ###
    # 1. X-Axis: Fixed start, expanding end.
    ax.set_xlim(first_date, current_date + pd.Timedelta(days=180)) # Add 6 months padding to the right

    # 2. Y-Axis: Rescale to fit all data shown *so far*.
    visible_df = df.iloc[:frame+1]
    min_price = visible_df['price'].min()
    max_price = visible_df['price'].max()
    ax.set_ylim(min_price * 0.95, max_price * 1.05) # 5% padding

    # DYNAMIC EVENT ANNOTATIONS
    for event in events:
        if not event['plotted'] and event['date'] <= current_date:
            event_row = df.iloc[(df['Date']-event['date']).abs().argsort()[:1]]
            event_price = event_row['price'].values[0]
            
            # Calculate offset dynamically based on current y-axis range
            y_range = max_price - min_price
            dynamic_offset = event['y_offset'] * y_range
            
            ax.annotate(event['label'],
                        xy=(event['date'], event_price),
                        xytext=(event['date'], event_price + dynamic_offset),
                        arrowprops=dict(arrowstyle="-", connectionstyle="arc3,rad=0.2", color="white", lw=0.8),
                        bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="gray", lw=0.5, alpha=0.7),
                        fontsize=9, ha='center')
            event['plotted'] = True

    # Update text displays
    date_text.set_text(f'Date: {current_date.strftime("%Y-%m-%d")}')
    price_text.set_text(f'Price: ${current_price:,.2f}')
    
    percentage_return = ((current_price - starting_price) / starting_price) * 100
    return_color = GREEN if percentage_return >= 0 else RED
    return_text.set_text(f'Total Return: {percentage_return:+.2f}%')
    return_text.set_color(return_color)

    return date_text, price_text, return_text

# --- 5. Create and Display the Animation ---
ani = FuncAnimation(fig, update, frames=len(df), interval=1, blit=False, repeat=False)
plt.show()