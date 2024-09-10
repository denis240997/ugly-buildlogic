from .cpm import cpm
from .utils import generate_sequence_by_est

def check_resources(sequence, operations, resources):
    schedule_start_times = {}

    for act in sequence:
        start_time = max([schedule_start_times.get(pre, 0) + operations[pre]['duration'] for pre in operations[act]['predecessors']], default=0)
        
        while True:
            resource_usage = {r: 0 for r in resources.keys()}
            conflict = False
            conflict_end_time = start_time

            for other_act, other_start in schedule_start_times.items():
                other_end = other_start + operations[other_act]['duration']

                if not (other_start >= start_time + operations[act]['duration'] or other_end <= start_time):
                    for r in operations[other_act]['resources']:
                        resource_usage[r] += 1

            for r in operations[act]['resources']:
                resource_usage[r] += 1

            for r in resources.keys():
                if resource_usage[r] > resources[r]:
                    conflict = True
                    conflict_end_time = max(conflict_end_time, other_end)
                    break

            if not conflict:
                break
            
            start_time = conflict_end_time

        schedule_start_times[act] = start_time

    return schedule_start_times

def rcpm(operations, df_resources):
    critical_path, _ = cpm(operations)
    resources = {res['type']: res['quantity'] for _, res in df_resources.iterrows()}
    sequence_by_est = generate_sequence_by_est(operations)
    schedule_start_times = check_resources(sequence_by_est, operations, resources)

    # Обновление всех времен
    for act, start_time in schedule_start_times.items():
        delta = start_time - operations[act]['early_start']
        operations[act]['early_start'] += delta
        operations[act]['early_finish'] += delta
        operations[act]['late_start'] += delta
        operations[act]['late_finish'] += delta

    total_duration = max(op['early_finish'] for op in operations.values())
    return critical_path, total_duration


