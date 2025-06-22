import functions_framework
import json
import random
import datetime

def interpret_preferred_date(preferred_date_str):
    today = datetime.date.today()
    if "today" in preferred_date_str.lower():
        return today.strftime("%A, %B %d, %Y")
    elif "tomorrow" in preferred_date_str.lower():
        return (today + datetime.timedelta(days=1)).strftime("%A, %B %d, %Y")
    elif "next monday" in preferred_date_str.lower():
        days_ahead = (0 - today.weekday() + 7) % 7
        if days_ahead == 0: days_ahead = 7
        return (today + datetime.timedelta(days=days_ahead)).strftime("%A, %B %d, %Y")
    elif "next tuesday" in preferred_date_str.lower():
        days_ahead = (1 - today.weekday() + 7) % 7
        if days_ahead == 0: days_ahead = 7
        return (today + datetime.timedelta(days=days_ahead)).strftime("%A, %B %d, %Y")
    elif "next wednesday" in preferred_date_str.lower():
        days_ahead = (2 - today.weekday() + 7) % 7
        if days_ahead == 0: days_ahead = 7
        return (today + datetime.timedelta(days=days_ahead)).strftime("%A, %B %d, %Y")
    return f"around {preferred_date_str}"


@functions_framework.http
def mock_schedule_appointment_tool(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    if request.method == 'POST':
        try:
            request_json = request.get_json(silent=True)
            if not request_json:
                return (json.dumps({"error": "Invalid JSON payload"}), 400, headers)

            preferred_date_str = request_json.get("preferred_date", "any available date")
            preferred_time_str = request_json.get("preferred_time", "any available time")
            reason = request_json.get("reason_for_appointment", "a general discussion")
            user_id = request_json.get("user_identifier", "User")

            mock_id = f"MOCKAPT-{random.randint(10000, 99999)}"
            processed_date_str = interpret_preferred_date(preferred_date_str)
            final_processed_date_time = f"{processed_date_str} {preferred_time_str if preferred_time_str != 'any available time' else ''}".strip()

            user_message = (f"Okay, I've provisionally scheduled a mock appointment for you regarding '{reason}' on {final_processed_date_time}. Your reference ID is {mock_id}.")
            employee_action_message = (f"Simulated internal action: An appointment request from '{user_id}' for '{reason}' "
                                       f"on {final_processed_date_time} (Ref: {mock_id}) has been noted. "
                                       f"A task will be created in monday.com for staff to confirm and add to their calendar.")

            response_data = {
                "user_confirmation_message": user_message,
                "simulated_employee_action_message": employee_action_message,
                "mock_appointment_id": mock_id,
                "processed_date_time": final_processed_date_time
            }
            return (json.dumps(response_data), 200, headers)
        except Exception as e:
            return (json.dumps({"error": f"An internal error occurred: {str(e)}"}), 500, headers)
    else:
        return (json.dumps({"error": "Method not allowed. Use POST."}), 405, headers)
