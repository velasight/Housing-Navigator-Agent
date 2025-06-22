import functions_framework
import json
import random

AFFORDABLE_HOUSING_PROGRAM_MAX_PRICE = 375000

@functions_framework.http
def set_affordable_property_alert_tool(request):
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

            user_id = request_json.get("user_identifier", "an unspecified user")
            location = request_json.get("location_preference", "any suitable area")
            property_type = request_json.get("property_type_preference", "any type")
            bedrooms_pref = request_json.get("bedrooms_preference")
            bedrooms = int(bedrooms_pref) if isinstance(bedrooms_pref, (int, float, str)) and str(bedrooms_pref).isdigit() else "any"
            bathrooms_pref = request_json.get("bathrooms_preference")
            bathrooms = int(bathrooms_pref) if isinstance(bathrooms_pref, (int, float, str)) and str(bathrooms_pref).isdigit() else "any"
            user_max_price_pref = request_json.get("max_desired_price")
            user_max_price = int(user_max_price_pref) if isinstance(user_max_price_pref, (int, float, str)) and str(user_max_price_pref).isdigit() else None
            other_features = request_json.get("other_features_preference", "no specific other features")

            mock_alert_id = f"MOCKALERT-{random.randint(10000, 99999)}"
            effective_max_price = AFFORDABLE_HOUSING_PROGRAM_MAX_PRICE
            price_message_segment = f"up to ${AFFORDABLE_HOUSING_PROGRAM_MAX_PRICE:,.0f} (aligned with program limits)"
            price_adjustment_note = ""

            if user_max_price is not None:
                if user_max_price < AFFORDABLE_HOUSING_PROGRAM_MAX_PRICE:
                    effective_max_price = user_max_price
                    price_message_segment = f"up to ${effective_max_price:,.0f}"
                elif user_max_price > AFFORDABLE_HOUSING_PROGRAM_MAX_PRICE:
                    price_adjustment_note = (f" (Note: Your preferred max price of ${user_max_price:,.0f} "
                                             f"has been adjusted to the program limit of ${AFFORDABLE_HOUSING_PROGRAM_MAX_PRICE:,.0f}.)")
            
            criteria_parts_for_user = []
            if isinstance(bedrooms, int):
                criteria_parts_for_user.append(f"{bedrooms}-bedroom")
            if isinstance(bathrooms, int):
                criteria_parts_for_user.append(f"{bathrooms}-bathroom")
            if property_type != "any type":
                 criteria_parts_for_user.append(property_type)
            criteria_parts_for_user.append(f"in {location}")
            criteria_parts_for_user.append(price_message_segment)
            if other_features != "no specific other features":
                criteria_parts_for_user.append(f"with features like '{other_features}'")
            
            criteria_summary_user = " ".join(criteria_parts_for_user)

            confirmation_message = (f"Okay {user_id}, I've set up a mock property alert for you for {criteria_summary_user}. "
                                    f"You'll be 'notified' of new matching listings.{price_adjustment_note} "
                                    f"Your alert ID is {mock_alert_id}.")

            alert_details_internal = (f"Mock Alert Set: User='{user_id}', Location='{location}', Type='{property_type}', "
                                      f"Beds='{bedrooms}', Baths='{bathrooms}', EffectiveMaxPrice='${effective_max_price:,.0f}', "
                                      f"OriginalUserMaxPrice='${user_max_price if user_max_price else 'N/A'}', "
                                      f"Features='{other_features}', AlertID='{mock_alert_id}'")

            response_data = {
                "alert_confirmation_message_for_user": confirmation_message,
                "alert_details_summary_internal": alert_details_internal,
                "mock_alert_id": mock_alert_id,
                "effective_max_price_for_alert": effective_max_price
            }
            
            return (json.dumps(response_data), 200, headers)
        except Exception as e:
            return (json.dumps({"error": f"An internal error occurred: {type(e).__name__} - {str(e)}"}), 500, headers)
    else:
        return (json.dumps({"error": "Method not allowed. Use POST."}), 405, headers)
