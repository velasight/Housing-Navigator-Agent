import functions_framework
import json
import math

ASSUMED_ANNUAL_INTEREST_RATE = 0.07
MOCK_DOWN_PAYMENT_ASSISTANCE_AMOUNT = 15000
PROGRAM_MAX_HOME_PRICE = 375000
MINIMUM_SUGGESTED_HOME_PRICE = 100000
MAX_TOTAL_DTI_RATIO = 0.43
ESTIMATED_MONTHLY_TAXES_INSURANCE_AS_PERCENT_OF_GMI = 0.08
MINIMUM_AFFORDABLE_MONTHLY_PI = 300

def calculate_loan_principal(monthly_payment, annual_interest_rate, loan_term_years):
    if annual_interest_rate <= 0: return 0
    monthly_interest_rate = annual_interest_rate / 12
    number_of_payments = loan_term_years * 12
    if (1 + monthly_interest_rate)**number_of_payments == 1: return 0
    principal = monthly_payment * (((1 + monthly_interest_rate)**number_of_payments - 1) /
                                 (monthly_interest_rate * (1 + monthly_interest_rate)**number_of_payments))
    return principal if principal > 0 else 0

def calculate_monthly_payment(principal, annual_interest_rate, loan_term_years):
    if principal <= 0: return 0
    if annual_interest_rate < 0: return 0
    monthly_interest_rate = annual_interest_rate / 12
    number_of_payments = loan_term_years * 12
    if number_of_payments == 0: return principal
    if monthly_interest_rate == 0: return principal / number_of_payments
    payment = principal * (monthly_interest_rate * (1 + monthly_interest_rate)**number_of_payments) / \
                        (((1 + monthly_interest_rate)**number_of_payments) - 1)
    return payment if payment > 0 else 0

@functions_framework.http
def estimate_home_affordability_tool(request):
    headers = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '3600'}
    if request.method == 'OPTIONS': return ('', 204, headers)
    if request.method == 'POST':
        try:
            request_json = request.get_json(silent=True)
            if not request_json: return (json.dumps({"error": "Invalid JSON payload"}), 400, headers)
            gmi = request_json.get("gross_monthly_income")
            monthly_debts = request_json.get("total_monthly_debt_payments", 0)
            user_dp = request_json.get("user_own_down_payment", 0)
            if gmi is None or not isinstance(gmi, (int, float)) or gmi <= 0: return (json.dumps({"error": "Valid gross_monthly_income is required."}), 400, headers)
            if not isinstance(monthly_debts, (int, float)) or monthly_debts < 0: monthly_debts = 0
            if not isinstance(user_dp, (int, float)) or user_dp < 0: user_dp = 0

            estimated_monthly_ti = gmi * ESTIMATED_MONTHLY_TAXES_INSURANCE_AS_PERCENT_OF_GMI
            max_monthly_piti_total_dti = (gmi * MAX_TOTAL_DTI_RATIO) - monthly_debts
            affordable_monthly_pi = max(0, max_monthly_piti_total_dti - estimated_monthly_ti)
            
            assumptions = (f"Estimates are based on an assumed annual interest rate of {ASSUMED_ANNUAL_INTEREST_RATE*100:.1f}%, a mock down payment assistance of ${MOCK_DOWN_PAYMENT_ASSISTANCE_AMOUNT:,.0f}, and an estimated ${estimated_monthly_ti:,.0f}/month for property taxes & homeowner's insurance. The P&I payment does not include taxes and insurance. This is not financial advice or a loan pre-approval.")

            if affordable_monthly_pi < MINIMUM_AFFORDABLE_MONTHLY_PI:
                message = ("Based on the information provided, the estimated affordable monthly payment for a home is quite low. To improve affordability, consider exploring ways to increase income, reduce existing monthly debts, or save for a larger personal down payment.")
                response_data = {"is_eligible_for_estimate": False, "message_to_user": message, "assumptions_made": assumptions}
                return (json.dumps(response_data), 200, headers)

            loan_principal_30yr = calculate_loan_principal(affordable_monthly_pi, ASSUMED_ANNUAL_INTEREST_RATE, 30)
            supported_home_price = loan_principal_30yr + MOCK_DOWN_PAYMENT_ASSISTANCE_AMOUNT + user_dp
            final_home_price = min(supported_home_price, PROGRAM_MAX_HOME_PRICE)
            price_cap_applied_note = ""
            if supported_home_price > PROGRAM_MAX_HOME_PRICE:
                price_cap_applied_note = (f" (Note: The estimated affordable home price was capped at ${PROGRAM_MAX_HOME_PRICE:,.0f} to align with program limits.)")

            if final_home_price < MINIMUM_SUGGESTED_HOME_PRICE:
                message = ("While there's some affordability indicated, the estimated home price is below typical market values for our programs. Consider discussing your situation with a housing counselor for more detailed guidance.")
                response_data = {"is_eligible_for_estimate": False, "message_to_user": message + price_cap_applied_note, "assumptions_made": assumptions}
                return (json.dumps(response_data), 200, headers)

            actual_loan_needed = max(0, final_home_price - MOCK_DOWN_PAYMENT_ASSISTANCE_AMOUNT - user_dp)
            payment_30yr = calculate_monthly_payment(actual_loan_needed, ASSUMED_ANNUAL_INTEREST_RATE, 30)
            payment_15yr = calculate_monthly_payment(actual_loan_needed, ASSUMED_ANNUAL_INTEREST_RATE, 15)
            price_range_low = max(MINIMUM_SUGGESTED_HOME_PRICE, math.floor(final_home_price * 0.95))
            price_range_high = final_home_price
            home_price_range_str = f"${price_range_low:,.0f} - ${price_range_high:,.0f}"
            
            message = (f"Okay! Based on your inputs, here's a simplified preliminary estimate:\n- Estimated Affordable Home Price Range: {home_price_range_str}{price_cap_applied_note}\n- Estimated Monthly Principal & Interest (P&I) for a 30-year loan: ${payment_30yr:,.2f}\n- Estimated Monthly Principal & Interest (P&I) for a 15-year loan: ${payment_15yr:,.2f}\n{assumptions}")
            
            response_data = {"is_eligible_for_estimate": True, "message_to_user": message, "estimated_home_price_range": home_price_range_str, "estimated_monthly_payment_30yr_pi": round(payment_30yr, 2), "estimated_monthly_payment_15yr_pi": round(payment_15yr, 2), "assumptions_made": assumptions}
            return (json.dumps(response_data), 200, headers)
        except Exception as e:
            return (json.dumps({"error": f"An internal error occurred: {type(e).__name__} - {str(e)}"}), 500, headers)
    else:
        return (json.dumps({"error": "Method not allowed. Use POST."}), 405, headers)
