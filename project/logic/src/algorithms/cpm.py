from collections import deque

def cpm(operations):
    
    # Инициализация ранних стартов и финишей
    for operation in operations.values():
        operation['early_start'] = 0
        operation['early_finish'] = 0

    # Прямой проход (Forward Pass)
    queue = deque([op_id for op_id, op in operations.items() if len(op['predecessors']) == 0])

    while queue:
        op_id = queue.popleft()

        operation = operations[op_id]
        operation['early_finish'] = operation['early_start'] + operation['duration']

        for succ_id in operation['successors']:
            successor = operations[succ_id]
            successor['early_start'] = max(successor['early_start'], operation['early_finish'])

            queue.append(succ_id)

    # Инициализация поздних стартов и финишей
    max_early_finish = max([op['early_finish'] for op in operations.values()])

    for operation in operations.values():
        operation['late_start'] = max_early_finish
        operation['late_finish'] = max_early_finish

    # Обратный проход (Backward Pass)
    queue = deque([op_id for op_id, op in operations.items() if len(op['successors']) == 0])

    while queue:
        op_id = queue.popleft()

        operation = operations[op_id]
        operation['late_start'] = operation['late_finish'] - operation['duration']

        for pred_id in operation['predecessors']:
            predecessor = operations[pred_id]
            predecessor['late_finish'] = min(predecessor['late_finish'], operation['late_start'])
            
            queue.append(pred_id)

    # Определение критического пути
    critical_path = []
    for op_id, operation in operations.items():
        if operation['early_start'] == operation['late_start']:
            operation['is_critical'] = True
            critical_path.append(op_id)

    # Общая длительность
    total_duration = max(op['early_finish'] for op in operations.values())

    return critical_path, total_duration