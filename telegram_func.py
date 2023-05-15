import datetime

def add_task(task_list, task_name, due_date):
    task_list[task_name] = due_date
    return task_list

def add_event(event_list, event_name, event_datetime):
    event_list[event_name] = event_datetime
    return event_list

def upload_file(file_list, file_id, file_name):
    file_list[file_id] = file_name
    return file_list

def delete_task(task_list, task_name):
    if task_name in task_list:
        del task_list[task_name]
    return task_list

def delete_event(event_list, event_name):
    if event_name in event_list:
        del event_list[event_name]
    return event_list

def delete_file(file_list, file_id):
    if file_id in file_list:
        del file_list[file_id]
    return file_list
