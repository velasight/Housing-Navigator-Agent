import functions_framework
import json

INCOME_CAP_80_AMI = 91360
REQUIRED_CITY_RESIDENCY = True

@functions_framework.http
def check_preliminary_eligibility_tool(request):
    headers = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '3600'}
    if request.method == 'OPTIONS': return ('', 204, headers)
    if request.method == 'POST':
        try:
            request_json = request.get_json(silent=True)
            if not request_json: return (json.dumps({"error": "Invalid JSON payload"}), 400, headers)
            user_id = request_json.get("user_identifier", "User")
            income_input = request_json.get("gross_annual_household_income")
            household_size_input = request_json.get("household_size")
            first_time_homebuyer_input = request_json.get("is_first_time_homebuyer")
            city_resident_input = request_json.get("is_city_resident")

            missing_fields = []
            if income_input is None: missing_fields.append("gross annual household income")
            if household_size_input is None: missing_fields.append("household size")
            if first_time_homebuyer_input is None: missing_fields.append("first-time homebuyer status")
            if city_resident_input is None: missing_fields.append("city residency status")

            if missing_fields:
                response_data = {"eligibility_status": "More Information Needed", "explanation": f"To perform a preliminary eligibility check, please provide your: {', '.join(missing_fields)}.", "criteria_considered": request_json}
                return (json.dumps(response_data), 200, headers)

            try:
                income = int(income_input)
                household_size = int(household_size_input)
                if not isinstance(first_time_homebuyer_input, bool):
                    if str(first_time_homebuyer_input).lower() in ['true', 'yes', '1']: first_time_homebuyer = True
                    elif str(first_time_homebuyer_input).lower() in ['false', 'no', '0']: first_time_homebuyer = False
                    else: raise ValueError("Invalid boolean string for is_first_time_homebuyer")
                else: first_time_homebuyer = first_time_homebuyer_input
                if not isinstance(city_resident_input, bool):
                    if str(city_resident_input).lower() in ['true', 'yes', '1']: city_resident = True
                    elif str(city_resident_input).lower() in ['false', 'no', '0']: city_resident = False
                    else: raise ValueError("Invalid boolean string for is_city_resident")
                else: city_resident = city_resident_input
                if income < 0 or household_size <= 0: raise ValueError("Income must be non-negative and household size must be positive.")
            except (ValueError, TypeError) as ve:
                response_data = {"eligibility_status": "More Information Needed", "explanation": f"Please provide valid inputs. Error: {str(ve)}", "criteria_considered": request_json}
                return (json.dumps(response_data), 200, headers)

            eligibility_status = "Potentially Eligible"
            explanation_lines = [(f"This is a preliminary, non-binding assessment for {user_id} based on an 80% AMI income limit of ${INCOME_CAP_80_AMI:,.0f} for the Atlanta-Sandy Springs-Roswell, GA HUD Metro FMR Area and the following inputs:"), f"- Gross Annual Household Income: ${income:,.0f}", f"- Household Size: {household_size}", f"- First-Time Homebuyer: {'Yes' if first_time_homebuyer else 'No'}", f"- City Resident: {'Yes' if city_resident else 'No'}"]

            if REQUIRED_CITY_RESIDENCY and not city_resident:
                eligibility_status = "Potentially Ineligible (Residency)"
                explanation_lines.append("Our current mock programs require city residency for this preliminary check.")
            elif income > INCOME_CAP_80_AMI:
                eligibility_status = "Potentially Ineligible (Income)"
                explanation_lines.append(f"Your household income of ${income:,.0f} may exceed the program's 80% AMI limit of ${INCOME_CAP_80_AMI:,.0f}.")
            else: 
                explanation_lines.append(f"Your income appears to be within the program's 80% AMI limit of ${INCOME_CAP_80_AMI:,.0f}.")
                if first_time_homebuyer: explanation_lines.append("Being a first-time homebuyer is often a positive factor.")
                if eligibility_status == "Potentially Eligible": explanation_lines.append("You show indicators for potential eligibility based on these simplified criteria. Further verification and official application are required.")
            
            explanation = " ".join(explanation_lines)
            response_data = {"eligibility_status": eligibility_status, "explanation": explanation, "criteria_considered": {"gross_annual_household_income": income, "household_size": household_size, "is_first_time_homebuyer": first_time_homebuyer, "is_city_resident": city_resident}}
            return (json.dumps(response_data), 200, headers)
        except Exception as e:
            return (json.dumps({"error": f"An internal error occurred: {type(e).__name__} - {str(e)}"}), 500, headers)
    else:
        return (json.dumps({"error": "Method not allowed. Use POST."}), 405, headers)
