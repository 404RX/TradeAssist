# Simple daily runner
#This is a simple script to run the momentum trading bot once daily.
# Simple_daily_runner.py
# To run: python -c "from advanced_trading_bot import run_momentum_bot; run_momentum_bot()"
# Or schedule with cron/Task Scheduler


from advanced_trading_bot import run_momentum_bot

# Run once daily at 10 AM ET
if __name__ == "__main__":
    print("Daily momentum trading run...")
    run_momentum_bot()

#Or use Windows Task Scheduler/cron to run:
#bash# Daily at 10 AM
#python -c "from advanced_trading_bot import run_momentum_bot; run_momentum_bot()"