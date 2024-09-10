import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ast

def plot_gantt_chart(results) -> None:
    gant_data = []
    
    for _, row in results.iterrows():
            gant_data.append({
                'Task': row['op_id'],
                'Start': row['early_start'],
                'Finish': row['early_finish'],
                'Critical': row.get('is_critical', False)
            })

    df_gant = pd.DataFrame(gant_data)

    plt.figure(figsize=(10, 6))

    for _, row in df_gant.iterrows():
        color = 'red' if row['Critical'] else 'blue'
        plt.barh(row['Task'], row['Finish'] - row['Start'], left=row['Start'], color=color)

    plt.xlabel('Time')
    plt.ylabel('Tasks')
    plt.title('Gantt Chart')
    plt.show()

def plot_gantt_and_resource_chart(results, resources) -> None:
    schedule = {row['op_id']: row['early_start'] for _, row in results.iterrows()}
    act_proc = {row['op_id']: row['duration'] for _, row in results.iterrows()}
    
    r_cap = {row['type']: row['quantity'] for _, row in resources.iterrows()}
    
    finish_times = {act: schedule[act] + act_proc[act] for act in schedule}
    total_time = max(finish_times.values())

    # Создаем графики
    _, axs = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [3, 1]})
    
    gant_data = []
    resource_colors = {} 

    colors = plt.cm.get_cmap('viridis', len(r_cap))

    for idx, (r, _) in enumerate(r_cap.items()):
        resource_colors[r] = colors(idx)

    for act, start_time in schedule.items():
        duration = act_proc[act]
        critical = results.loc[results['op_id'] == act, 'is_critical'].values[0]
        color = 'red' if critical else 'blue'
        axs[0].barh(act, duration, left=start_time, color=color, edgecolor='black')
        gant_data.append({
            'Task': act,
            'Start': start_time,
            'Finish': start_time + duration,
            'Critical': critical
        })

    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Tasks')
    axs[0].set_title('Gantt Chart (with resources)')
    
    axs[0].set_xlim(0, total_time)
    axs[1].set_xlim(0, total_time)
    
    resource_usage = {r: np.zeros(total_time + 1) for r in r_cap}
    for _, row in results.iterrows():
        act = row['op_id']
        start = schedule[act]
        end = start + act_proc[act]
        resources_list = ast.literal_eval(row['resources']) if isinstance(row['resources'], str) else row['resources']
        for r in resources_list:
            resource_usage[r][start:end] += 1

    legend_handles = [] 
    for r, usage in resource_usage.items():
        color = resource_colors[r]
        line, = axs[1].plot(usage, drawstyle='steps-post', color=color, label=f'Resource {r}')
        axs[1].axhline(y=r_cap[r], linestyle='--', linewidth=1, color=color) 
        legend_handles.append(line)

    axs[1].set_ylim(0, max(r_cap.values()) + 1)
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Resource Utilization')
    
    axs[1].legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    
    axs[1].grid(True)

    plt.tight_layout()
    plt.subplots_adjust(right=0.85)
    plt.show()

