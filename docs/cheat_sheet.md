# Smolagents Tool Development Cheat Sheet

## 🎯 Core Principle
**The best agentic systems are the simplest** - reduce LLM calls and complexity at every opportunity.

## 📋 Essential Checklist

### ✅ Tool Design
- [ ] **Single responsibility** - Does ONE thing well
- [ ] **Minimal parameters** - Only essential inputs
- [ ] **Clear naming** - Function and parameter names are self-explanatory
- [ ] **Combine related operations** - Group multiple API calls into one tool when possible

### ✅ Documentation
- [ ] **Precise docstring** - Exact format requirements for each parameter
- [ ] **Input examples** - Show exactly what valid inputs look like
- [ ] **Output format** - Clear description of return format

### ✅ Error Handling
- [ ] **Descriptive error messages** - Tell LLM exactly what went wrong
- [ ] **Format validation** - Check inputs and give specific correction guidance
- [ ] **Actionable failures** - Error messages tell user how to fix the problem

### ✅ Logging
- [ ] **Print key steps** - Use `print()` statements throughout execution
- [ ] **Log failures** - Print what was tried and why it failed
- [ ] **Success confirmation** - Print when operations succeed

## 🛠️ Code Template

```python
from smolagents import tool

@tool
def my_tool(param: str) -> str:
    """
    Brief description of what the tool does.
    
    Args:
        param: Exact description with format requirements.
               Example: "Date in format 'YYYY-MM-DD' like '2024-01-15'"
    
    Returns:
        str: Description of output format
    """
    print(f"Starting operation with: {param}")
    
    # Validate input format
    try:
        # validation logic
        pass
    except Exception as e:
        error_msg = f"Invalid format for param. Expected 'YYYY-MM-DD', got '{param}'. Error: {e}"
        print(error_msg)
        return error_msg
    
    try:
        # main logic
        result = do_operation(param)
        print(f"Operation successful: {result}")
        return f"Success: {result}"
        
    except Exception as e:
        error_msg = f"Operation failed: {e}. Try checking [specific thing to check]"
        print(error_msg)
        return error_msg
```

## 🚫 What NOT to Do

### ❌ Over-Engineering
```python
# BAD - Too complex, multiple responsibilities
@tool
def advanced_weather_system(location, date, include_forecast=True, 
                           units="metric", detailed=False, cache=True):
```

```python
# GOOD - Simple, focused
@tool
def get_weather(location: str, date: str) -> str:
```

### ❌ Poor Error Messages
```python
# BAD - Unhelpful
return "Error occurred"

# GOOD - Actionable
return "Date format invalid. Use 'YYYY-MM-DD' format like '2024-01-15'"
```

### ❌ No Logging
```python
# BAD - Silent execution
def process_data(data):
    result = api_call(data)
    return result

# GOOD - Logged execution
def process_data(data):
    print(f"Processing data: {data}")
    result = api_call(data)
    print(f"API call successful: {result}")
    return result
```

## 🎨 Parameter Guidelines

### ✅ Good Parameter Descriptions
```python
location: str
    """Location name in format 'City, Country' like 'Paris, France' or 'New York, USA'"""

date_time: str
    """Date and time as 'MM/DD/YY HH:MM:SS' like '01/15/24 14:30:00'"""

file_path: str
    """Full path to file like '/home/user/document.txt' or relative path like 'data/file.csv'"""
```

### ❌ Poor Parameter Descriptions
```python
location: str
    """The location"""  # Too vague

date: str
    """Date string"""  # No format specified

path: str
    """File path"""  # No examples
```

## 🔄 Tool Combination Strategy

### ✅ Combine Related Operations
```python
# GOOD - One tool for related data
@tool
def get_surf_spot_info(location: str) -> str:
    """Get weather AND travel distance for surf spot."""
    weather = weather_api(location)
    distance = distance_api(location)
    return f"Weather: {weather}\nDistance: {distance}"
```

### ❌ Separate Simple Operations
```python
# BAD - Forces multiple LLM calls
@tool
def get_weather(location: str) -> str:
    """Get weather only."""

@tool  
def get_distance(location: str) -> str:
    """Get distance only."""
```

## 💡 Pro Tips

### 1. **The "Dumb User" Test**
Ask yourself: *"If I was using this tool for the first time and wasn't very smart, could I easily use it and fix my mistakes?"*

### 2. **Print Everything Important**
```python
print(f"Input received: {param}")
print(f"Attempting operation...")
print(f"API response: {response}")
print(f"Final result: {result}")
```

### 3. **Validate Early, Fail Fast**
```python
# Check input format before doing expensive operations
if not re.match(r'\d{4}-\d{2}-\d{2}', date):
    return "Invalid date format. Use YYYY-MM-DD like '2024-01-15'"
```

### 4. **Return Structured, Readable Output**
```python
# GOOD
return f"Weather for {location} on {date}: Temperature {temp}°C, Rain {rain}%, Wind {wind}mph"

# BAD
return str([temp, rain, wind])  # Hard to parse
```

## 🎯 Quick Validation

Before deploying your tool, check:
1. Can the LLM understand what went wrong from error messages?
2. Are parameter requirements crystal clear?
3. Does the tool do exactly one thing well?
4. Would a beginner know how to fix their mistakes?
5. Is execution logged for debugging?

## 📚 Remember

> **"How easy would it be for me, if I was dumb and using this tool for the first time ever, to program with this tool and correct my own errors?"**

This is the ultimate test for smolagents tool quality.