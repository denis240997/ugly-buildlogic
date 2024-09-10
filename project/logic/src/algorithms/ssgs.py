from .cpm import cpm

def ssgs(operations, df_resources, use_pr=False):
    critical_path, _ = cpm(operations)
    resources = {res['type']: res['quantity'] for _, res in df_resources.iterrows()}

    start_times = {}
    finish_times = {}
    scheduled = []
    max_time = sum(op['duration'] for op in operations.values())
    resource_availability = {r: [resources[r]] * max_time for r in resources.keys()}

    while len(scheduled) < len(operations):
        eligible_activities = [act for act in operations if act not in scheduled and all(pre in scheduled for pre in operations[act]['predecessors'])]

        if not eligible_activities:
            print('!!! The schedule cannot be done !!!')
            break

        # min-lft приоритет
        if use_pr:
            pr = {act: operations[act]['late_finish'] for act in eligible_activities}
            current_act = min(pr, key=pr.get)
        else:
            current_act = eligible_activities[0]

        earliest_start = max(finish_times.get(pre, 0) for pre in operations[current_act]['predecessors']) if operations[current_act]['predecessors'] else 0
        duration = operations[current_act]['duration']

        eligible_times = []
        for t in range(earliest_start, max_time):
            if all(resource_availability[r][t:t + duration].count(resources[r]) >= duration for r in operations[current_act]['resources']):
                eligible_times.append(t)

        if eligible_times:
            start_time = min(eligible_times)
            finish_time = start_time + duration
            start_times[current_act] = start_time
            finish_times[current_act] = finish_time
            scheduled.append(current_act)

            for r in operations[current_act]['resources']:
                for time_slot in range(start_time, finish_time):
                    resource_availability[r][time_slot] -= 1
        else:
            print(f"Operation {current_act} cannot added in the schedule.")
            
    # Обновление всех времен
    for act, start_time in start_times.items():
        delta = start_time - operations[act]['early_start']
        operations[act]['early_start'] += delta
        operations[act]['early_finish'] += delta
        operations[act]['late_start'] += delta
        operations[act]['late_finish'] += delta

    total_duration = max(op['early_finish'] for op in operations.values())
    return critical_path, total_duration


def local_ssgs(operations, df_resources, selected_tasks, use_pr=True):

    resources = {res['type']: res['quantity'] for _, res in df_resources.iterrows()}
    max_time = sum(op['duration'] for op in operations.values())
    resource_availability = {r: [resources[r]] * max_time for r in resources.keys()}   

    for act, op in operations.items():
        if act not in selected_tasks:
            for r in op['resources']:
                for time_slot in range(op['early_start'], op['early_finish']):
                    resource_availability[r][time_slot] -= 1

    start_times = {}
    finish_times = {}
    scheduled = []
    
    selected_operations = {task: operations[task] for task in selected_tasks}

    while len(scheduled) < len(selected_operations):
        eligible_activities = [act for act in selected_operations if act not in scheduled]

        if not eligible_activities:
            print('!!!The schedule cannot be updated!!!')
            break

        # min-lft приоритет
        if use_pr:
            pr = {act: selected_operations[act]['late_finish'] for act in eligible_activities}
            current_act = min(pr, key=pr.get)
        else:
            current_act = eligible_activities[0]

        earliest_start = max(finish_times.get(pre, 0) for pre in selected_operations[current_act]['predecessors']) if selected_operations[current_act]['predecessors'] else 0
        duration = selected_operations[current_act]['duration']

        eligible_times = []
        for t in range(earliest_start, max_time):
            if all(resource_availability[r][t:t + duration].count(resources[r]) >= duration for r in selected_operations[current_act]['resources']):
                eligible_times.append(t)

        if eligible_times:
            start_time = min(eligible_times)
            finish_time = start_time + duration
            start_times[current_act] = start_time
            finish_times[current_act] = finish_time
            scheduled.append(current_act)

            for r in selected_operations[current_act]['resources']:
                for time_slot in range(start_time, finish_time):
                    resource_availability[r][time_slot] -= 1
        else:
            print(f"Operation {current_act} cannot added in the schedule.")

            
    # Обновление всех времен
    for act, start_time in start_times.items():
        delta = start_time - operations[act]['early_start']
        operations[act]['early_start'] += delta
        operations[act]['early_finish'] += delta
        operations[act]['late_start'] += delta
        operations[act]['late_finish'] += delta

    total_duration = max(op['early_finish'] for op in operations.values())
    return total_duration
