import pandas as pd
import re
import time

#Validates for integer (used for user input in menu)
def Validate_Text(text):
    try:
        response = int(text)
        return response
    except ValueError:
        return

#Asks the user if they would like to change the selected input (used in bad words file selection)
def Ask_For_Removal(previous, text, yes_message):
    response = input(f"{text}")
    possible_responses = ["y","n"]
    while True:
        if response.lower() == possible_responses[0]:
            return input(f"{yes_message}")
        elif response.lower() == possible_responses[1]:
            return previous
        else:
            print("Invalid input, please try again")

#Opens text file and saves it to memory
def Open_Text_File():
    #global variables to access outside scope
    global df
    global file_selected
    #Asks user to select a file
    file_selected = input("Enter a file name (Excluding .txt file extension): ")
    #Initializes "lines"
    lines = None
    try:
        #Opens the file specified
        with open(f"{file_selected}.txt", "r") as f:
            #sets lines = lines in user-selected file
            lines = [line.strip() for line in f]
        #creates a dataframe with those lines
        df = pd.DataFrame(lines, columns=["chat"])
        print("File Found")
    except Exception as e:
        #If file cannot be found or error opening file
        print(f"Error opening file: {e}")
        #sets these variables to None if file cant be opened
        file_selected = None
        df = None

def Detect_Bad_Words():
    #global variable (so it can be accessed in Display_Bad_Words function)
    global bad_words_df
    global bad_words_file
    #returns if no chat file selected beforehand
    if df is None:
        print("No chat file loaded.")
        return
    #asks for bad words file
    if not bad_words_file:
        bad_words_file = input("Enter bad words file name (Excluding .txt file extension): ")
    else:
        bad_words_file = Ask_For_Removal(bad_words_file, "Would you like to remove the previous bad words file? (Y/N)", "Enter a new bad words file name (Excluding .txt file extension):")
    try:
        #Opens bad words file
        with open(f"{bad_words_file}.txt", "r") as f:
            #sets content to content of file (all lowercase)
            content = f.read().lower()
            #creates a list for the bad words
            bad_words_list = [word.strip() for word in content.split(",") if word.strip()]
        #creates escape to match any literal strings with regex expressions: https://stackoverflow.com/questions/280435/escaping-regex-string
        escape = [re.escape(word) for word in bad_words_list]
        #creates a pattern
        pattern_string = r'\b('+'|'.join(escape) + r')\b'
        #compiles into regex object using pattern (more efficient?): https://www.geeksforgeeks.org/python/re-compile-in-python/
        bad_words_pattern = re.compile(pattern_string, re.IGNORECASE)
        print("Bad words file loaded successfully.")
    except Exception as e:
        #prints error if cant find bad words file
        print(f"Error loading bad words file: {e}")
        return
    #initializes results
    results = []
    #loop for iterating through chat df
    for index, row in df.iterrows():
        line = row["chat"]
        #creates matches and if it finds the selected pattern in the file, keeps track
        matches = bad_words_pattern.findall(line)
        if matches:
            for match in matches:
                results.append({"line_num": index,"bad_word": match.lower(),"frequency": 1,"text": line})
    #if results exist
    if results:
        #creates a df for bad words
        bad_words_df = pd.DataFrame(results)
        bad_words_df = bad_words_df.groupby(["line_num", "bad_word", "text"]).count().reset_index()
        #renames the column to "frequency". https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html
        bad_words_df.rename(columns={"frequency": "count"}, inplace=True)
        print("Bad words detected in chat file")
    else:
        #if no bad words are found, sets bad_words_df to None
        bad_words_df = None
        print("No bad words found.")

def Display_Bad_Words():
    #will return if there is no bad words in the selected chat file
    if bad_words_df is None or bad_words_df.empty:
        print("No results to display.")
        return
    #prints the appropriate summary
    print(f"{spacer} Summary (word: total count) {spacer}")
    summary = bad_words_df.groupby("bad_word")["count"].sum().reset_index()
    summary = summary.sort_values(by="bad_word")
    #prints the count of how many times each bad word appeared
    for _, row in summary.iterrows():
        print(f'{row["bad_word"]}: {row["count"]}')
    #prints a more detailed view (showing the line the bad word appeared in)
    print(f"{spacer} Details {spacer}")
    detailed = bad_words_df.sort_values(by="line_num")
    for _, row in detailed.iterrows():
        print(f'Line {row["line_num"]} — word: "{row["bad_word"]}" — {row["text"]}')

def Exit():
    #global variable (setting to false ends the main loop)
    global running
    running = False
    print("Exiting...")

running = True
spacer = "****************"
file_selected = None
bad_words_file = None
df = None
bad_words_df = None

#dictionary that stores the options and the functions
options_dict = {
    1: Open_Text_File,
    2: Detect_Bad_Words,
    3: Display_Bad_Words,
    4: Exit
}

#Main loop (main menu logic)
def Main_Loop():
    while running:
        print(spacer)
        if not file_selected:
            print("No file loaded.")
        else:
            print(f"Current loaded file: {file_selected}.txt")
        print("1) Open Text File\n2) Detect Bad Words\n3) Display Bad Words\n4) Exit")
        response = Validate_Text(input(""))
        if (response) in options_dict:
            options_dict[response]()
        else:
            print("Invalid Response, Please Try Again...")
        #added a delay, because having no delay may confuse the user
        time.sleep(0.5)

#initiates main loop
Main_Loop()
