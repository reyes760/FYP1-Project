from datetime import datetime
import price_db

class PriceRecord:
    def __init__(self, title, price_type, daily_rate, deposit, start_date, end_date, user_id, vehicle_id):
        self.title = title
        self.price_type = price_type
        self.daily_rate = daily_rate
        self.deposit = deposit
        self.start_date = start_date
        self.end_date = end_date
        self.user_id = user_id
        self.vehicle_id = vehicle_id

    def calculate_duration(self):
        """Calculates the number of days for this price setting."""
        d1 = datetime.strptime(self.start_date, "%Y-%m-%d")
        d2 = datetime.strptime(self.end_date, "%Y-%m-%d")
        return abs((d2 - d1).days)

    def get_total_potential_revenue(self):
        """Calculates total revenue based on duration and daily rate."""
        days = self.calculate_duration()
        return days * self.daily_rate

    def save(self):
        """Saves this object to the database via price_db."""
        data = {
            'title': self.title,
            'price_type': self.price_type,
            'daily_rate': self.daily_rate,
            'deposit': self.deposit,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'user_id': self.user_id,
            'vehicle_id': self.vehicle_id
        }
        price_db.insert_revenue_record(data)
        print(f"Success: Price record '{self.title}' saved.")

# Example Usage:
if __name__ == "__main__":
    # Initialize the table
    price_db.init_db()

    # Create a new record instance
    new_price = PriceRecord(
        title="Ramadan Special",
        price_type="Seasonal",
        daily_rate=150.00,
        deposit=200.00,
        start_date="2026-03-01",
        end_date="2026-03-31",
        user_id=1,
        vehicle_id=101
    )

    # Save to DB
    new_price.save()
    
    # Logic check
    print(f"Potential Revenue: RM{new_price.get_total_potential_revenue()}")