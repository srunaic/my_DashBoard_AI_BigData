import pandas as pd

# --- CONSTANTS (Company Standard) ---
TROY_OZ_TO_G = 31.1035   # Standard Troy Ounce to Grams
DON_TO_G = 3.75          # Standard 1 Don to Grams

def get_gold_don_price_krw(usd_oz, exchange_rate):
    """
    Calculates the price of Gold per 1 Don in KRW.
    
    Formula:
      Gold(KRW/Don) = (Gold(USD/oz) / 31.1035) * 3.75 * USD/KRW
    
    Args:
        usd_oz (float): Gold price in USD per Troy Ounce.
        exchange_rate (float): USD/KRW exchange rate.
        
    Returns:
        float: Price in KRW per 1 Don.
    """
    if usd_oz is None or exchange_rate is None:
        return None
    
    gram_price_usd = usd_oz / TROY_OZ_TO_G
    don_price_usd = gram_price_usd * DON_TO_G
    don_price_krw = don_price_usd * exchange_rate
    
    return don_price_krw

def get_silver_don_price_krw(usd_oz, exchange_rate):
    """
    Calculates the price of Silver per 1 Don in KRW.
    Uses the same standard logic as Gold.
    """
    return get_gold_don_price_krw(usd_oz, exchange_rate)

if __name__ == "__main__":
    # Internal Unit Test
    test_gold = 2000.0 # $2000/oz
    test_rate = 1300.0 # 1300 KRW/$
    
    # Expected: (2000 / 31.1035) * 3.75 * 1300
    # = 64.3014 * 3.75 * 1300 = 241.13 * 1300 = ~313,469 KRW
    
    result = get_gold_don_price_krw(test_gold, test_rate)
    print(f"Test Calculation:")
    print(f"Gold ${test_gold}/oz @ {test_rate} KRW/$ => {result:,.2f} KRW/Don")
    
    expected = (2000 / 31.1035) * 3.75 * 1300
    assert abs(result - expected) < 0.01, "Calculation Logic Error!"
    print("Unit Test Passed.")
