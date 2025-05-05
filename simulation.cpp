/*Str Index = Index to test in Yahoo finance format
Str StartDate = day to start testing on (should be varied to have more accurate testing)
Str EndDate = day to stop testing on (should be varied to have more accurate testing)
Float Interval = trading / data feeding interval in days
Str CurrentDay = StartDate
Array Positions = list of Position objs
Float StartBalance = amount of money to start with
Float Equity = currently available money

Class Position:
Str Id = UUID for identification
Str Type = "Buy"/"Sell"
Float EntryPoints = points at entry
Int ContractsNumber = how many stocks or contracts were bought
Array Buffer = array for storing additional data between algorithm calls

- Pull Index data from StartDate to EndDate.
 - Loop from startDate to endDate with Interval:
   - CurrentDay += Interval
   - call algorithm with data from startDate to currentDay and Positions
   - Execute actions (close, open positions)*/