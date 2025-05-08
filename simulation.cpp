/*Str Index = Index to test in Yahoo finance format
Str StartDate = day to start testing on (should be varied to have more accurate testing)
Str EndDate = day to stop testing on (should be varied to have more accurate testing)
Float Interval = trading / data feeding interval in days
Str CurrentTime = StartDate
Array Positions = list of Position objs
Float StartBalance = amount of money to start with
Float Equity = currently available money

Class Position:
Str Id = UUID for identification
Str Type = "Buy"/"Sell"
Float EntryPoints = points at entry
Int ContractsNumber = how many stocks or contracts were bought
Array Buffer = array for storing additional data between algorithm calls

Class CloseAction:
Str Id = UUID of Position
Float ExitPoints = points on exit

Class OpenAction:
Str Type = "Buy"/"Sell"
Int ContractsNumber = How many stocks or contracts were bought

- Pull Index data from StartDate to EndDate.
- Loop from startDate to endDate with Interval:
  - CurrentTime += Interval
  - EntryPoints = points at currentTime
  - call algorithm with data from startDate to currentTime and Positions
  - Execute actions for loop:
    - If CloseAction:
      - Profit = ExitPoints-EntryPoints * ContractsNumber
      - Equity += Profit
      - Delete Position from Positions
    - If OpenAction:
      - Expense = EntryPoints * ContractsNumber
      - Equity -= Expense
      - uuid = GENERATE ID
      - New Position in Positions(uuid, Type, EntryPoints, ContractsNumber)*/

# include <iostream>
# include <string>
# include <ctime>
# include <vector>
# include <cstdlib>
# include "DateTimeUtilities.h"

using namespace std;

int main() {
  class Position {
    public:
      std::string id;
      std::string type;
      float entryPoints;
      int contractsNumber;
      std::string buffer[5];
  };

  class CloseAction {
    public:
    std::string id;
    float exitPoints;
  };

  class OpenAction {
    public:
      std::string type;
      int contractsNumber;
  };

  std::string startDate = "2024-06-05 00:00:00+09:00"; //Must be "YYYY-MM-DD HH:mm:SS+TH:TM"
  std::string endDate = "2025-06-05 00:00:00+09:00"; 
  std::string Index = "^GSPC"; //Yahoo finance indicator
  std::string Interval = "4h"; //Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 4h, 1d, 5d, 1wk, 1mo, 3mo]
  float startBalance = 10000;

  std::vector<Position> Positions;
  std::string startDateUTC = DateTimeUtils::convertToUTCString(startDate);
  std::string endDateUTC = DateTimeUtils::convertToUTCString(endDate);
  float Equity = startBalance;

  std::string pull_command = ".venv\\Scripts\\python.exe get_data.py \"" + startDateUTC + "\" \"" + endDateUTC + "\" " + Interval;
  std::cout << pull_command;
  system(pull_command.c_str());

  for (std::string currentTime = startDateUTC; currentTime < endDateUTC; currentTime = DateTimeUtils::addIntervalToDate(currentTime, Interval)) {
    
  }
  
  std::cout << "Start balance was: " << startBalance << "\n";
  std::cout << "Equity is: " << Equity << "\n";
  std::cout << "Profit is: " << Equity-startBalance << "\n";
  return 0;
}