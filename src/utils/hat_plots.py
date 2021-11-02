import matplotlib.pyplot as plt


def plot_hydropotential(df):
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Flow rate (cu.ft/s)', color=color)
    ax1.plot(df['Streamflow, ft&#179;/s'], label="Flow rate", color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Efficiency (%)', color=color)  # we already handled the x-label with ax1
    ax2.plot(df['efficiency (%)'],'b-',label="Power", color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
    plt.title("Yearly flow data from USGS and potential power")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #plt.savefig(os.path.join('..','fig','usgs_twin_falls_flow_power.jpg'))
    plt.show()

    return None
    

def plot_discharge(df):
    return None