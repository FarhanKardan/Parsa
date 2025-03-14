class PaymentCalculator:
    def __init__(self, mobile_models, payment_options, guarantee_options, installment_months, interest_rates):
        self.mobile_models = mobile_models
        self.payment_options = payment_options
        self.guarantee_options = guarantee_options
        self.installment_months = installment_months
        self.interest_rates = interest_rates

    def calculate_payments(self, user_data):
        """Calculate payment details based on user data."""
        mobile_model = user_data["mobile_model"]
        mobile_price = user_data["mobile_price"]
        upfront_percentage = user_data["upfront_percentage"]
        upfront_amount = user_data["upfront_amount"]
        remaining_balance = user_data["remaining_balance"]
        guarantee_type = user_data["guarantee_type"]
        installment_months = user_data["installment_months"]

        # Get interest rate based on payment and guarantee
        payment_percentage = f"{int(upfront_percentage * 100)}%"
        interest_rate = self.interest_rates.get((payment_percentage, guarantee_type), 0)

        # Calculate interest and monthly payments
        total_interest = remaining_balance * interest_rate * installment_months
        total_amount_due = remaining_balance + total_interest
        monthly_payment = total_amount_due / installment_months

        response = (
            f"✅ شما انتخاب کردید: {mobile_model}\n"
            f"💰 قیمت: {mobile_price:,.2f}\n"
            f"💵 پیش‌پرداخت: {upfront_amount:,.2f} ({payment_percentage})\n"
            f"🛒 مبلغ باقی‌مانده: {remaining_balance:,.2f}\n"
            f"📜 نوع ضمانت: {guarantee_type}\n"
            f"📆 دوره اقساط: {installment_months} ماه\n"
            f"💲 نرخ سود ماهانه: {interest_rate * 100:.1f}%\n"
            f"📈 کل سود: {total_interest:,.2f}\n"
            f"💳 مبلغ پرداختی ماهانه: {monthly_payment:,.2f}\n"
            f"💸 مجموع مبلغ پرداختی: {total_amount_due:,.2f}"
        )
        return response