import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import telegram_func as tgf
from db import Database

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize database
db = Database()

def start(update: Update, context):
    # Introduce the bot and show the available functions
    user_name = update.effective_message.from_user.first_name
    text = f"Hello, {user_name}! I'm your remote team management bot. Here are the available functions:"
    keyboard = [
        [InlineKeyboardButton("Add Task", callback_data="add_task"), InlineKeyboardButton("Task List", callback_data="task_list")],
        [InlineKeyboardButton("Add Event", callback_data="add_event"), InlineKeyboardButton("Event List", callback_data="event_list")],
        [InlineKeyboardButton("Upload File", callback_data="upload_file"), InlineKeyboardButton("File List", callback_data="file_list")],
        [InlineKeyboardButton("Delete Task", callback_data="delete_task"), InlineKeyboardButton("Delete Event", callback_data="delete_event"), InlineKeyboardButton("Delete File", callback_data="delete_file")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(text, reply_markup=reply_markup)

def handle_callback(update: Update, context: CallbackContext, event_name=None, event_date=None):
    query = update.callback_query
    query.answer()

    if query.data == "add_task":
        reply_keyboard = [['2023-04-25', '2023-04-26'], ['2023-04-27', '2023-04-28'], ['2023-04-29', '2023-04-30']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        query.message.reply_text("Please select the task deadline:", reply_markup=markup)
        context.user_data["state"] = "add_task"

    elif query.data == "task_list":
        tasks = db.get_tasks_by_user_id(update.effective_user.id)
        if tasks:
            text = "Here are your tasks:\n\n"
            for task in tasks:
                text += f"Task Name: {task['title']}\nDeadline: {task['due_date']}\n\n"
            update.effective_message.reply_text(text)
        else:
            update.effective_message.reply_text("No tasks found.")

    elif query.data == "add_event":
        update.effective_message.reply_text("Please enter the event name:")
        context.user_data["state"] = "add_event_name"
        db.add_event(update.effective_user.id, event_name, event_date)

    elif query.data == "event_list":
        events = db.get_events_by_user_id(update.effective_user.id)
        if events:
            text = "Here are your events:\n\n"
            for event in events:
                text += f"Event Name: {event['name']}\nDate: {event['date_time']}\n\n"
            update.effective_message.reply_text(text)
        else:
            update.effective_message.reply_text("No events found.")

    elif query.data == "upload_file":
        update.effective_message.reply_text("Please send the file you want to upload:")
        context.user_data["state"] = "upload_file"

    elif query.data == "file_list":
        files = db.get_files_by_user_id(update.effective_user.id)
        if files:
            text = "Here are your files:\n\n"
            for file in files:
                text += f"File ID: {file['file_id']}\n\n"
            update.effective_message.reply_text(text)
        else:
            update.effective_message.reply_text("No files found.")

    elif query.data == "delete_task":
        tasks = db.get_tasks_by_user_id(update.effective_user.id)
        if tasks:
            keyboard = [[InlineKeyboardButton(task["title"], callback_data=f"delete_task_{task['id']}")] for task in
                        tasks]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.effective_message.reply_text("Select a task to delete:", reply_markup=reply_markup)
        else:
            update.effective_message.reply_text("No tasks found.")

    elif query.data.startswith("delete_task_"):
        task_id = int(query.data.split("_")[-1])
        db.delete_task_from_db(task_id)
        update.effective_message.reply_text("Task deleted.")

    elif query.data == "delete_event":
        events = db.get_events_by_user_id(update.effective_user.id)
        if events:
            keyboard = [[InlineKeyboardButton(event["name"], callback_data=f"delete_event_{event['id']}")] for event in
                        events]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.effective_message.reply_text("Select an event to delete:", reply_markup=reply_markup)
        else:
            update.effective_message.reply_text("No events found.")

    elif query.data.startswith("delete_event_"):
        event_id = int(query.data.split("_")[-1])
        db.delete_event_from_db(event_id)
        update.effective_message.reply_text("Event deleted.")

    elif query.data == "delete_file":
        files = db.get_files_by_user_id(update.effective_user.id)
        if files:
            keyboard = [[InlineKeyboardButton(file["file_id"], callback_data=f"delete_file_{file['id']}")] for file in
                        files]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.effective_message.reply_text("Select a file to delete:", reply_markup=reply_markup)
        else:
            update.effective_message.reply_text("No files found.")

    elif query.data.startswith("delete_file_"):
        file_id = int(query.data.split("_")[-1])
        db.delete_file_from_db(file_id)
        update.effective_message.reply_text("File deleted.")

def handle_reply(update: Update, context: CallbackContext):
    user = update.message.from_user
    state = context.user_data.get("state")

    if state == "add_task":
        task_deadline = update.message.text
        context.user_data["task_deadline"] = task_deadline
        update.message.reply_text("Please enter the task name:")
        context.user_data["state"] = "add_task_name"

    elif state == "add_task_name":
        task_name = update.message.text
        task_deadline = context.user_data.get("task_deadline")
        db.add_task(user.id, task_name, task_deadline)
        update.message.reply_text(f"Task '{task_name}' with deadline '{task_deadline}' has been added.")
        context.user_data["state"] = None

    elif state == "add_event":
        event_date = update.message.text
        context.user_data["event_date"] = event_date
        update.message.reply_text("Please enter the event name:")
        context.user_data["state"] = "add_event_name"

    elif state == "add_event_name":
        event_name = update.message.text
        update.message.reply_text("Please enter the event date:")
        context.user_data["event_name"] = event_name
        context.user_data["state"] = "add_event_date"

    elif state == "add_event_date":
        event_date = update.message.text
        event_name = context.user_data.get("event_name")
        if event_name is not None and event_date is not None:
            db.add_event(user.id, event_name, event_date)
            update.message.reply_text(f"Event '{event_name}' with date '{event_date}' has been added.")
        else:
            update.message.reply_text("Error: event name or date is missing.")
        context.user_data["state"] = None

def main():
    token = "5884394290:AAHSK-A43E-IhrI2wqF5Ylsi6p_otLwpe8E"
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    dp.add_handler(MessageHandler(Filters.text | Filters.document, handle_reply))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()