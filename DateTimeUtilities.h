#ifndef DATETIME_UTILS_H
#define DATETIME_UTILS_H

#include <string>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <cmath>
#include <unordered_map>

namespace DateTimeUtils {

    // Days in each month (non-leap year)
    const int daysInMonth[] = {
        31, 28, 31, 30, 31, 30,
        31, 31, 30, 31, 30, 31
    };

    bool isLeapYear(int year) {
        return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
    }

    int daysInGivenMonth(int year, int month) {
        if (month == 2 && isLeapYear(year))
            return 29;
        return daysInMonth[month - 1];
    }

    void normalizeDateTime(int& year, int& month, int& day, int& hour, int& minute, int& second) {
        // Normalize seconds
        minute += second / 60;
        second %= 60;
        if (second < 0) { second += 60; minute--; }

        // Normalize minutes
        hour += minute / 60;
        minute %= 60;
        if (minute < 0) { minute += 60; hour--; }

        // Normalize hours
        day += hour / 24;
        hour %= 24;
        if (hour < 0) { hour += 24; day--; }

        // Normalize days
        while (day > daysInGivenMonth(year, month)) {
            day -= daysInGivenMonth(year, month);
            month++;
            if (month > 12) {
                month = 1;
                year++;
            }
        }

        while (day < 1) {
            month--;
            if (month < 1) {
                month = 12;
                year--;
            }
            day += daysInGivenMonth(year, month);
        }
    }

    std::string convertToUTCString(const std::string& datetime) {
        std::string normalized = datetime;
        std::string tz = "+00:00";  // default timezone
    
        if (normalized.length() == 19) {
            normalized += tz;
        } else if (normalized.length() == 25 && normalized[10] == ' ' && (normalized[19] == '+' || normalized[19] == '-')) {
            tz = normalized.substr(19, 6);
        } else {
            throw std::invalid_argument("Invalid datetime format");
        }
    
        // Parse datetime
        int year   = std::stoi(normalized.substr(0, 4));
        int month  = std::stoi(normalized.substr(5, 2));
        int day    = std::stoi(normalized.substr(8, 2));
        int hour   = std::stoi(normalized.substr(11, 2));
        int minute = std::stoi(normalized.substr(14, 2));
        int second = std::stoi(normalized.substr(17, 2));
    
        // Parse timezone offset
        int tz_sign = (tz[0] == '-') ? -1 : 1;
        int tz_hour = std::stoi(tz.substr(1, 2)) * tz_sign;
        int tz_min  = std::stoi(tz.substr(4, 2)) * tz_sign;
    
        // Subtract timezone offset to get UTC
        hour   -= tz_hour;
        minute -= tz_min;
    
        normalizeDateTime(year, month, day, hour, minute, second);
    
        // Format result with +00:00 offset
        std::ostringstream oss;
        oss << std::setw(4) << std::setfill('0') << year << "-"
            << std::setw(2) << month << "-"
            << std::setw(2) << day << " "
            << std::setw(2) << hour << ":"
            << std::setw(2) << minute << ":"
            << std::setw(2) << second
            << "+00:00";
    
        return oss.str();
    }
    

    bool isFirstAfter(const std::string& dt1, const std::string& dt2) {
        std::string utc1 = convertToUTCString(dt1);
        std::string utc2 = convertToUTCString(dt2);
        return utc1 > utc2; // Lexicographical comparison is valid for YYYY-MM-DD HH:MM:SS
    }

    std::string addIntervalToDate(const std::string& datetime, const std::string& interval) {
        if (datetime.length() != 25 || datetime[10] != ' ' || (datetime[19] != '+' && datetime[19] != '-'))
            throw std::invalid_argument("Invalid datetime format");
    
        int year   = std::stoi(datetime.substr(0, 4));
        int month  = std::stoi(datetime.substr(5, 2));
        int day    = std::stoi(datetime.substr(8, 2));
        int hour   = std::stoi(datetime.substr(11, 2));
        int minute = std::stoi(datetime.substr(14, 2));
        int second = std::stoi(datetime.substr(17, 2));
    
        std::string tz = datetime.substr(19, 6);
    
        // Fixed-length intervals in seconds
        static const std::unordered_map<std::string, int> intervalSeconds = {
            {"1m", 60}, {"2m", 120}, {"5m", 300}, {"15m", 900}, {"30m", 1800},
            {"60m", 3600}, {"90m", 5400},
            {"1h", 3600}, {"2h", 7200}, {"4h", 14400}, {"12h", 43200},
            {"1d", 86400}, {"5d", 432000}, {"1wk", 604800}
        };
    
        // Month-based calendar intervals
        static const std::unordered_map<std::string, int> intervalMonths = {
            {"1mo", 1}, {"3mo", 3}
        };
    
        if (auto it = intervalSeconds.find(interval); it != intervalSeconds.end()) {
            second += it->second;
        } else if (auto it = intervalMonths.find(interval); it != intervalMonths.end()) {
            month += it->second;
        } else {
            throw std::invalid_argument("Unsupported interval format: " + interval);
        }
    
        normalizeDateTime(year, month, day, hour, minute, second);
    
        std::ostringstream oss;
        oss << std::setw(4) << std::setfill('0') << year << "-"
            << std::setw(2) << month << "-"
            << std::setw(2) << day << " "
            << std::setw(2) << hour << ":"
            << std::setw(2) << minute << ":"
            << std::setw(2) << second
            << tz;
    
        return oss.str();
    }
    


}

#endif // DATETIME_UTC_CONVERTER_H
