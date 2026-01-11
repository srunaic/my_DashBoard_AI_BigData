class PremiumCalculator:
    def __init__(self):
        # Thresholds defined in Design Document
        self.thresholds = {
            "DISCOUNT": 0.0,
            "NORMAL": 3.5,
            "HIGH": 5.5
        }

    def calculate_premium(self, domestic_price, theoretical_price):
        """
        Calculates the premium between domestic physical price and international theoretical price.
        
        Args:
            domestic_price (float): Real physical retail price (KRW).
            theoretical_price (float): Calculated paper price (KRW).
            
        Returns:
            dict: {
                'amount': float,
                'rate': float (percentage),
                'status': str,
                'message': str
            }
        """
        if theoretical_price == 0 or theoretical_price is None:
            return None
        
        diff = domestic_price - theoretical_price
        rate = (diff / theoretical_price) * 100
        
        status = "Normal"
        message = "Stable Market"
        
        if rate < self.thresholds["DISCOUNT"]:
            status = "Discount"
            message = "Unusual: Domestic Price Lower (Liquidity need?)"
        elif rate < self.thresholds["NORMAL"]:
            status = "Normal"
            message = "Standard Operational Premium"
        elif rate < self.thresholds["HIGH"]:
            status = "High Demand"
            message = "Anxiety: Physical Accumulation"
        else:
            status = "Overheating"
            message = "Panic: Extreme Currency Distrust"
            
        return {
            'amount': diff,
            'rate': rate,
            'status': status,
            'message': message
        }
