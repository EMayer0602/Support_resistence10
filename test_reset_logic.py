#!/usr/bin/env python3
"""
Test script to verify the missing data counter resets correctly when data becomes available again.
"""

def mock_get_backtest_price_with_reset(symbol, date_str, field):
    """
    Mock function that simulates some missing data followed by available data.
    Missing data for 5 days, then available, then missing again.
    """
    # Simulate missing data for dates 2025-07-05 to 2025-07-09 (5 days)
    # Then data available for 2025-07-10, 2025-07-11
    # Then missing again for 2025-07-12 onwards
    missing_dates_1 = ["2025-07-05", "2025-07-06", "2025-07-07", "2025-07-08", "2025-07-09"]
    missing_dates_2 = ["2025-07-12", "2025-07-13", "2025-07-14", "2025-07-15", "2025-07-16", "2025-07-17", "2025-07-18"]
    
    if date_str in missing_dates_1 + missing_dates_2:
        print(f"{symbol}: keine Daten für {date_str}")
        return None
    else:
        return 100.0  # Mock price


def mock_generate_trades_for_day_with_reset(date_str):
    """
    Mock version using the reset scenario price data.
    """
    mock_tickers = {"AAPL": {"trade_on": "Close"}, "MSFT": {"trade_on": "Close"}}
    
    trades = []
    any_data_found = False

    for symbol, cfg in mock_tickers.items():
        field = cfg.get("trade_on", "Close").capitalize()
        price = mock_get_backtest_price_with_reset(symbol, date_str, field)
        if price is None:
            continue
        
        any_data_found = True
        trades.append({
            "symbol": symbol,
            "side": "BUY",
            "qty": 100,
            "price": price
        })

    return trades, any_data_found


def test_reset_counter_logic():
    """
    Test that the missing days counter resets correctly when data becomes available.
    """
    print("🧪 Testing missing days counter reset logic...")
    from datetime import datetime, timedelta
    
    def mock_date_range(start="2025-07-01", end="2025-07-18"):
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        days = []
        while start_date <= end_date:
            days.append(start_date.strftime("%Y-%m-%d"))
            start_date += timedelta(days=1)
        return days
    
    # Test the logic
    backtest_trades = {}
    missing_days = 0
    max_missing_days = 10
    processed_days = 0
    reset_occurred = False
    
    for date_str in mock_date_range("2025-07-01", "2025-07-18"):
        processed_days += 1
        trades, any_data_found = mock_generate_trades_for_day_with_reset(date_str)
        backtest_trades[date_str] = trades
        
        if not any_data_found:
            missing_days += 1
            print(f"📅 {date_str}: Keine Kursdaten für alle Ticker gefunden (Tag {missing_days} ohne Daten)")
            
            if missing_days >= max_missing_days:
                print(f"\n⚠️ BACKTEST ABGEBROCHEN: {max_missing_days} aufeinanderfolgende Tage ohne Kursdaten für alle Ticker.")
                break
        else:
            if missing_days > 0:
                reset_occurred = True
                print(f"📅 {date_str}: {len(trades)} Trades erzeugt. (Counter reset: {missing_days} -> 0)")
            else:
                print(f"📅 {date_str}: {len(trades)} Trades erzeugt.")
            missing_days = 0  # Reset counter when data found
    
    print(f"\n✅ Test abgeschlossen. Verarbeitete Tage: {processed_days}")
    print(f"   Counter reset occurred: {reset_occurred}")
    
    # Should reach the end since the counter resets and never reaches 10 consecutive days
    if processed_days == 18 and reset_occurred:
        print("✅ ERFOLG: Counter wurde korrekt zurückgesetzt, wenn Daten verfügbar waren.")
        return True
    else:
        print("❌ FEHLER: Counter Reset logic funktioniert nicht wie erwartet.")
        return False


if __name__ == "__main__":
    success = test_reset_counter_logic()
    exit(0 if success else 1)