#!/usr/bin/env python3
"""
Test script to verify the endless loop fix logic works correctly.
This tests the missing data tracking without needing full IB/market data setup.
"""

def mock_get_backtest_price(symbol, date_str, field):
    """
    Mock function that simulates price data availability.
    Returns None for certain date ranges to simulate missing data.
    """
    # Simulate missing data for dates 2025-07-05 to 2025-07-15 (11 consecutive days)
    missing_dates = [
        "2025-07-05", "2025-07-06", "2025-07-07", "2025-07-08", "2025-07-09",
        "2025-07-10", "2025-07-11", "2025-07-12", "2025-07-13", "2025-07-14", "2025-07-15"
    ]
    
    if date_str in missing_dates:
        print(f"{symbol}: keine Daten für {date_str}")
        return None
    else:
        return 100.0  # Mock price


def mock_generate_trades_for_day(date_str):
    """
    Mock version of generate_trades_for_day that uses mock price data.
    """
    mock_tickers = {"AAPL": {"trade_on": "Close"}, "MSFT": {"trade_on": "Close"}}
    
    trades = []
    any_data_found = False

    for symbol, cfg in mock_tickers.items():
        field = cfg.get("trade_on", "Close").capitalize()
        price = mock_get_backtest_price(symbol, date_str, field)
        if price is None:
            continue
        
        any_data_found = True
        # Mock trade creation
        trades.append({
            "symbol": symbol,
            "side": "BUY",
            "qty": 100,
            "price": price
        })

    return trades, any_data_found


def mock_generate_backtest_date_range(start="2025-07-01", end="2025-07-18"):
    """Mock version of generate_backtest_date_range"""
    from datetime import datetime, timedelta
    
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    days = []

    while start_date <= end_date:
        days.append(start_date.strftime("%Y-%m-%d"))
        start_date += timedelta(days=1)

    return days


def test_endless_loop_fix():
    """
    Test that the endless loop fix works correctly.
    This should abort after 10 consecutive days without data.
    """
    print("🧪 Testing endless loop fix logic...")
    
    # Test the logic that would be in the main backtest loop
    import json
    backtest_trades = {}
    missing_days = 0
    max_missing_days = 10
    processed_days = 0
    
    for date_str in mock_generate_backtest_date_range("2025-07-01", "2025-07-18"):
        processed_days += 1
        trades, any_data_found = mock_generate_trades_for_day(date_str)
        backtest_trades[date_str] = trades
        
        if not any_data_found:
            missing_days += 1
            print(f"📅 {date_str}: Keine Kursdaten für alle Ticker gefunden (Tag {missing_days} ohne Daten)")
            
            if missing_days >= max_missing_days:
                print(f"\n⚠️ BACKTEST ABGEBROCHEN: {max_missing_days} aufeinanderfolgende Tage ohne Kursdaten für alle Ticker.")
                print(f"   Letzter verarbeiteter Tag: {date_str}")
                print(f"   Möglicherweise sind die Ticker delisted oder der Datumsbereich liegt außerhalb der verfügbaren Daten.")
                print(f"   Bisherige Trades wurden in trades_by_day.json gespeichert.")
                break
        else:
            missing_days = 0  # Reset counter wenn Daten gefunden wurden
            print(f"📅 {date_str}: {len(trades)} Trades erzeugt.")
    
    print(f"\n✅ Test abgeschlossen. Verarbeitete Tage: {processed_days}")
    print(f"   Erwartung: Sollte bei Tag 14 (2025-07-14) abbrechen, da dann 10 Tage ohne Daten erreicht sind.")
    print(f"   Tatsächlich: Abbruch bei Tag {processed_days}")
    
    # Verify the logic worked correctly
    if processed_days == 14:  # Should stop at 2025-07-14 (day 14) 
        print("✅ ERFOLG: Endlos-Schleife wurde korrekt nach 10 aufeinanderfolgenden Tagen ohne Daten beendet.")
        return True
    else:
        print("❌ FEHLER: Logic funktioniert nicht wie erwartet.")
        return False


if __name__ == "__main__":
    success = test_endless_loop_fix()
    exit(0 if success else 1)