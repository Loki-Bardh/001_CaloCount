# CALO_COUNT - A basic calorie counter

## Video Demo:  <[Calo-Count Walkthrough](https://youtu.be/H77wYvgKe7k)>

## Table of Contents:

1. [Concept](#concept)
2. [Project Description](#project-description)
3. [Components & Features](#components-&-features)
4. [Resources & Credit](#resources-&-credit)


### Concept

The concept is pretty straightforward, a simple web-based app that allows the user to find, adjust, log, and track their calories over time.
It, however, didn't start out that way, where a considerably more ambitious scope was laid out. Eventually, as the work got underway, the functionality was refined and whittled down to a simpler and more manageable first MVP. The largest challenge throughout the process was to be wary of scope creep and to keep the MVP to its core elements.


### Project Description:

The user is required to create a very simple account to access the app, and though a contact email is required, it does not currently need to be an active contact. Once the account is created, the user can explore the various parts of the app that allow them to search for a variety of different foods using a REST API sourced from the United States Agriculture Department, that provides the nutrient information used by the app. Currently, the focus is on the main groups of interest when it comes to nutrition:
    - Serving Size
    - Calories
    - Fats and Lipids
    - Proteins
    - Carbohydrates
    - Sugars (Sucrose, Fructose, Glucose, etc)
    - Salt
The user can save their meals as part of their profile in order to track their food consumption and nutrient intake. A simple averages function allows them to also see daily averages calculated across different time periods. It is possible to see a brief history of the items eaten, and as a fun addition, the user can also see what foods they have eaten the most often or the most of! The app was kept to limited functionality as a first attempt at a coding project, yet with a core concept that could easily be grown into a much more interactive and personal experience accompanying the user through their day-to-day habits.
This project was created using the tools and skills developed during CS50, which led to the choice of Python for the backend, Jinja and Flask for passing information between back and front, JavaScript for the dynamic elements that were needed, guided by ChatGPT, HTML & CSS for the front-end UI, and then SQLite3 for the local database requirements.


### Components & Features

1. Register, Login, Logout
   - Registering is simple and though it requires an email, it does not need to be active or real for the time being. This was for futurproof inclusion and testing.
   - Password is not kept locally and is saved as a generated hash. No password recovery is included for the time being.
   - Session logs are essential for the functioning of the app, but are removed whenever a session is closed.

2. Profile Page (accessed by clicking the cupcake logo)
   - Gives the current day's averages as well as the date, type, and calorie count of the last meal logged.

3. Calorie Calculator
   - This page has a search functionality that goes through the USDA Food database API to provide options for either ingredients or meals. Branded items have been
     excluded for the time being in order to simplifiy the available options and quicken the search. When the appropriate item is found, it can be added by selecting the checkbox.
   - There is an option for the user to fill in the details manually as per the product label. This is then added to the table along with any items that where searched.
   - The items/ingredients listed in the table can be adjusted for serving size or removed completely from the selection.
   - Once all the items are selected, the user still needs to determine the type of meal (breakfast, lunch, dinner, or snack) before it can be saved into the local
     database.
   - When the meal is saved there is an automatic redirect to the Profile Page.

4. Averages
   - Here the main nutrients are displayed along with their unit of measurement(metric) for a quick view by the user:
                - Serving Size in grams (g)
                - Calories in kilo calories (kCal)
                - Fats and Lipids in grams (g)
                - Proteins in grams (g)
                - Carbohydrates in grams (g)
                - Sugars (Sucrose, Fructose, Glucose, etc) in grams (g)
                - Salt in milligrams (g)
   - There are selectable time frames that allow the user to see the daily averages for each of the above. These are as follows and are based on the current date:
                - Today
                - Last 7 Days
                - This Month
                - Last 3 Months
                - Last 6 Months
                - Last 12 Months
   - To ensure accuracy of the average, there is also a counter informing the user how many days have been logged during the selected time frame. Though it does not
      differentiate whether all meals were logged, it still provides a more accurate gauge of nutrient intake over selected time.

5. Top 5 Foods
   This is a fun little component that was created to add a bit of play into the app, essentially allowing the user to see the top 5 food items that they have consumed.
   - The user can select by "Eaten Most Often" which will select the five items in their saved database that they consumed the most times, sorting by occurence.
   - Or the user can select "Eaten the Most" which will return the top 5 items that have the largest sum of serving size.
   Eventually this could be grown to provide either a few more details on each item or add other search parameters to the sorting.

6. 7 Day History
   This last functionality allows the user to see all of the items that have been logged over the last 7 days and see each of their attributes. It also provides a direct link to the USDA search page provdiding the full details of the items and all of its nutrients and values.

#### Resources & Credit
This project was made possible thanks to the help of AI through the Harvard CS50 Ducky and ChatGPT. The core idea remains mine but both tools were used as sound boards and to help provide deeper understanding of various functions. Whilst ChatGPT was helpful to provide basic templates and principles of more complex dynamic functions and code, Ducky was completely invaluable. He provided extensive help when it came to troubleshooting and helping to debug the code. Both were also used at various stages to help streamline the code and get a better understanding of conventions that are used when programming.
The US Departement of Agriculure has a fantastic API, and whilst there were a few challenges in getting to grips with the ends and to understand the finer details of how to exploit the API, the documentaion was accessible and very complete. Here is a link to the site where anyone can freely apply for their own API key should they wish:
                                    [USDA FoodData Central](https://fdc.nal.usda.gov/)

This was a lot of fun and a fantastic learning curve, thank you to Harvard's CS50 course!
