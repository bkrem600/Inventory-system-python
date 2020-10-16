# Libraries that are used in this code are imported here
import easygui
from easygui import *
import datetime
from time import gmtime, strftime
import sys
import json
import os
import pickle


# create class Component - for storing attributes about the components within a batch, stored as a dictionary
# attributes for this class include the date, component type, size, status and finish of each component and a unique serial number
class Component:
    # create a new instance for component
    def __init__(self, manufacture_date, component_type, serial, size, status, finish):
        self.manufacture_date = manufacture_date
        self.component_type = component_type
        self.serial = serial
        self.size = size
        self.status = status
        self.finish = finish

    # a method to add this component to a particular batch
    # every attribute of the component class is passed through this method except for the serial parameter
    def pick_component(self, batch):
        batch.add_component(self.manufacture_date, self.component_type, self.size, self.status, self.finish)

    # This code is used to return a human readable output of a class object, helpful for testing purposes
    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


# create class Batch - for storing attributes about each batch
# attributes for this class include the amount of components in a batch, a list of all the component serial numbers, storage location and a unique batch number
# certain attributes of the batch class are not applied through the paramters but instead through the "add_component" method
class Batch:
    # initialisation method
    def __init__(self, batch_number, amount_components, serial_numbers, location):
        # initialise components in the batch
        self.batch_number = batch_number
        self.manufacture_date = ""
        self.component_type = ""
        self.size = ""
        self.amount_components = amount_components
        self.serial_numbers = serial_numbers
        self.batch_status = []
        self.location = location

    # This method applies attributes to the Batch class from the Component class
    # 5 parameters are received from the "pick_component" method and applied to the batch class here
    # the "batch_status" attribute is a list of the concatenated value of status and finish with a string in between
    def add_component(self, manufacture_date, component_type, size, status, finish):
        self.manufacture_date = manufacture_date
        self.component_type = component_type
        self.size = size
        self.batch_status = self.batch_status + [status + "-" + finish]

    # This code is used to return a human readable output of a class object, helpful for testing purposes
    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


# This function is used to get a string value of the location of the "Data" directory for storing and loading files
def get_data_directory():
    # Get the "current working directory" to locate the BatchIndex json file
    cwd = os.getcwd()

    # the variable "data_directory" removes the last 4 letters from the string which is "Code" and replaces with "Data\\"
    data_directory = cwd[:-4] + "Data\\"
    return data_directory
    # "os.getcwd()" SOURCE: https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
    # We found this code that gets a string of the current working directory and used it to locate our data folder


# This function is used to restore the BatchIndex.json file in the case it has been corrupted or deleted
# This code exists as a function as it is repeatedly called on to check the validity of the batch index file
def restore_batch_index(data_directory):
    # "os.listdir()" SOURCE: https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    # We found this code which lists all the files in a directory which we use throughout the program in different ways
    list_of_files = os.listdir(data_directory)
    amount_of_files = len(list_of_files)
    list_of_batches = []

    # The minimum amount of files that should exist for a batch is 2 and 3 if you include the index file
    if amount_of_files > 3:
        for x in range(0, amount_of_files):
            # This code is checking to see if any of the files in the list match the criteria for a batch file including the file type and length of the file name
            if list_of_files[x][12:16] == ".pck" and len(list_of_files[x]) == 16:
                # Attempts to convert any matching filenames to integers since a batch file should not contain any letters or non integer characters
                # If conversion is successful, it is added to the list of batches, if it fails the list stays the same
                try:
                    int(list_of_files[x][0:12])
                    list_of_batches = list_of_batches + [list_of_files[x][0:12]]
                except ValueError:
                    list_of_batches = list_of_batches

    # If batch files are located then they are added to the BatchIndex.json file
    if len(list_of_batches) > 0:
        with open(data_directory + "BatchIndex.json", 'w') as outfile:
            json.dump(list_of_batches, outfile)

        if list_of_batches == []:
            return None
        else:
            return list_of_batches

    # If no batches are found then we just dump the basic [] to the file
    else:
        with open(data_directory + "BatchIndex.json", 'w') as outfile:
            json.dump([], outfile)
        return None


# This function is used to open the BatchIndex.json file for use in the program
# This code exists as a function so that it can be repeatedly called on whenever needed
def get_batch_index():

    # Calling this function returns the location of the "Data" folder
    data_directory = get_data_directory()

    # "os.path.isfile()" SOURCE: https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
    # We found this code which checks if a file exists which helps prevent errors from crashing the program
    # If the BatchIndex.json file does not exist then it is created here with only the [] data in it
    if not os.path.isfile(data_directory + 'BatchIndex.json'):
        with open(data_directory + "BatchIndex.json", "a+") as outfile:
            json.dump([], outfile)
        # This function is called to restore and potentially populate the new BatchIndex.json file
        restore_batch_index(data_directory)

    # The "index_errors" variable is declared as the integer 0 to represent no errors
    # Each time a problem is found with the batch file, for example incorrect formatting or unaccepted characters, the "index_errors" variable is increased by 1 for each error
    index_errors = 0

    # The file is opened with the read function instead of load which allows us to inspect the file without causing the program to return an error
    with open(data_directory + "BatchIndex.json") as json_file:
        read_json_file = json_file.read()

    # This checks if the file simply has [] in it which is a correct but empty json file and attempts to restore/populate it
    if len(read_json_file) == 2 and read_json_file[0] == "[" and read_json_file[1] == "]":
        restore_batch_index(data_directory)
    # If the file is empty then an error is found
    elif len(read_json_file) == 0:
        index_errors = index_errors + 1
    # If the file is less than the minimum length possible for a batch number to exist but in the correct format, an error is found
    elif len(read_json_file) < 16 and read_json_file[0] == "[" and read_json_file[-1] == "]":
        index_errors = index_errors + 1
    # If the file has less than two bits in it, an error is found
    elif len(read_json_file) < 2:
        index_errors = index_errors + 1
    # If the file does not start and end with [ and ] then an error is found
    elif read_json_file[0] != "[" or read_json_file[-1] != "]":
        index_errors = index_errors + 1
    # If the file is in the correct format then the program checks for unaccepted characters
    elif read_json_file[0] == "[" and read_json_file[-1] == "]":
        # If the second and second last character in the file is " then characters are checked, else an error is found
        if read_json_file[1] == '"' and read_json_file[-2] == '"':
            for x in range(2, len(read_json_file) - 2):
                # If any letters are found then an error is found
                if read_json_file[x].isupper() or read_json_file[x].islower():
                    index_errors = index_errors + 1
                else:
                    # If any bits cannot be converted to integers (batch numbers) then an error is found
                    try:
                        int(read_json_file[x])
                    except ValueError:
                        if read_json_file[x] == '"' or read_json_file[x] == "," or read_json_file[x] == " ":
                            index_errors = index_errors
                        else:
                            index_errors = index_errors + 1
        else:
            index_errors = index_errors + 1

    # If no errors are found then the batch index file is opened and loaded into a variable
    if index_errors == 0:
        with open(data_directory + "BatchIndex.json") as json_file:
            json_data = json.load(json_file)
        return json_data
    # If errors are found then restoration is attempted
    else:
        restore_batch_index(data_directory)


# The purpose of this function is to save a json file with an index of batch numbers used
def save_index(batch_number):

    data_directory = get_data_directory()
    json_data = get_batch_index()

    # If the json_data variable is not empty, it means it has batch numbers in it and the current one is added to that list
    if json_data is not None and json_data != []:
        data = json_data + [batch_number]
        with open(data_directory + "BatchIndex.json", 'w') as outfile:
            json.dump(data, outfile)
    # If it is empty then the variable is set to the current batch number in a list
    else:
        data = [batch_number]
        with open(data_directory + "BatchIndex.json", 'w') as outfile:
            json.dump(data, outfile)


# The purpose of this function is to generate the next batch number based on previously used numbers
def new_batch_number(manufacture_date):
    json_data = get_batch_index()

    # "str().zfill()" SOURCE: https://stackoverflow.com/questions/339007/nicest-way-to-pad-zeroes-to-a-string
    # We found the code snippet above which allows us to pad the batch numbers with zero's to make the correct format

    # This if statement detects whether or not the file is empty, if it is the batch number is the current date and 1
    if json_data is not None and json_data != []:
        # Get last batch number, identify its date, identify the last serial and calculate the next in the sequence
        last_batch_number = json_data[-1]
        last_batch_date = last_batch_number[0:8]
        last_batch_serial = int(last_batch_number[8:12])
        next_batch_serial = last_batch_serial + 1

        # If the last batch number is the current date, the number is increased by one (if it's less than the maximum)
        if last_batch_date == manufacture_date:
            next_batch_number = manufacture_date + str(next_batch_serial).zfill(4)
            return next_batch_number

        # If the last batch number is not the current date, then the next batch number is the current date starting at 1
        elif last_batch_date != manufacture_date:
            next_batch_number = manufacture_date + str(1).zfill(4)
            return next_batch_number

    else:
        next_batch_number = manufacture_date + str(1).zfill(4)
        return next_batch_number


# This function is called in the main function and is used to create the batch using classes
def create_batch():

    # this variable is used to establish whether the user has confirmed the batch details or not, by default it is False
    confirm = False

    # This loop is used to allow the user to correct any incorrect details they may have entered
    while confirm is False:
        # "datetime.datetime.today().strftime()" SOURCE: https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python
        manufacture_date = datetime.datetime.today().strftime('%Y%m%d')
        # This function is called to generate the batch number with the date generated above but returns it with a unique number also
        batch_number = new_batch_number(manufacture_date)
        msgbox("Your batch number is: " + batch_number, "Create a new batch")
        size = ""
        formatted_date = ""
        # The default location for batches is declared here
        location = "Factory Floor - Warehouse Not Allocated"
        # An integer box is used as this limits inputs to integers within a range we have set
        amount = integerbox("How many components are in this batch (1 to 9999)?", "Amount of components", lowerbound=1,
                            upperbound=9999)

        # If the user selects "cancel" or closes the message box, they are given the opportunity to return to the menu
        if amount is None:
            check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
            if check is True:
                break

        if amount is not None:
            # This code warns the user that they made need to adjust the size of the message box to see the OK button
            if amount >= 20 and amount is not None:
                msgbox("WARNING: Due to the large quantity of components, you may need to adjust the size of message boxes if you are unable to locate the 'OK' button at the bottom of the box.", "WARNING", "OK")

            # This code warns the user that generating large amounts of components can take a few moments
            if amount >= 100 and amount is not None:
                msgbox("WARNING: Large quantities of components may take longer for the program to generate and load.", "WARNING", "OK")

        # 3 components stored as a list and using a choicebox limits their input to just those 3 choices
        component_types = ["Winglet Attachment Strut", "Door Seal Clamp Handle", "Rudder Pivot Pin"]
        component_type = choicebox("Select the component type: ", "Select Component Type", component_types)

        # If the user selects "cancel" or closes the message box, they are given the opportunity to return to the menu
        if component_type is None:
            check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
            if check is True:
                break

        # The code below is used get the size/fitment type from the user depending on their choice of component type
        if component_type == "Winglet Attachment Strut":
            sizes = ["A320 Series", "A380 Series"]
            size = choicebox("Select the component fitment type:", "Select Fitment Type", sizes)
            if size is not None:
                # string formatting SOURCE: book titled "Python For Everyone"
                # The formatting used below for the message boxes is used throughout the program to make it easier to read
                message = ("%20s %s" % ("Quantity:", str(amount))) + "\n" + \
                          ("%20s %s" % ("Component type:", component_type)) + "\n" + \
                          ("%20s %s" % ("Fitment type:", size))
                confirm = ynbox("This batch contains the following details:" + "\n" + "\n" + "-"*50 + "\n" + "\n" +
                                message + "\n" + "\n" + "-"*50 + "\n" + "\n" +
                                "Are these batch details correct?", "Confirm batch", ["Yes", "No"])
                if confirm is None:
                    check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
                    if check is True:
                        break
            else:
                check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
                if check is True:
                    break

        elif component_type == "Door Seal Clamp Handle":
            message = ("%20s %s" % ("Quantity:", str(amount))) + "\n" + \
                      ("%20s %s" % ("Component type:", component_type))
            confirm = ynbox("This batch contains the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                            message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                            "Are these batch details correct?", "Confirm batch", ["Yes", "No"])
            if confirm is None:
                check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
                if check is True:
                    break

        elif component_type == "Rudder Pivot Pin":
            sizes = ["10mm diameter x 75mm length", "12mm diameter x 100mm length", "16mm diameter x 150mm length"]
            size = choicebox("Select the component size:", "Select Size", sizes)

            if size is not None:
                message = ("%20s %s" % ("Quantity:", str(amount))) + "\n" + \
                          ("%20s %s" % ("Component type:", component_type)) + "\n" + \
                          ("%20s %s" % ("Component size:", size))
                confirm = ynbox("This batch contains the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                "Are these batch details correct?", "Confirm batch", ["Yes", "No"])
                if confirm is None:
                    check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
                    if check is True:
                        break
            else:
                check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
                if check is True:
                    break

        # If the user confirms the batch details we move on to the creation and printing phase
        if confirm is True:
            # This code (SOURCE: detailed above) is used to generate the current date and time which is when the batch is created
            now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            msgbox("Batch and component records created at " + now, "Batch Records")

            # Checks if the user would like to print the batch details
            batch_details = ynbox("Would you like to print the batch details?", "Print batch details", ["Yes", "No"])
            if batch_details is None:
                check = ynbox("Would you like to return to the menu?", "Cancel batch creation", ["Yes", "No"])
                if check is True:
                    break

            # This code is used to format the batch manufacture date into a more readable form but doesn't change its stored value
            if manufacture_date != "":
                formatted_date = manufacture_date[0:4] + "-" + manufacture_date[4:6] + "-" + manufacture_date[6:8]

            # If the user wants to print batch details, the details are printed differently depending on the component type
            if batch_details is True and component_type == "Winglet Attachment Strut":
                # python for everyone book source
                message = ("%25s %s" % ("Batch number:", batch_number)) + "\n" + \
                          ("%25s %s" % ("Location:", location)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", component_type)) + "\n" + \
                          ("%25s %s" % ("Fitment type:", size)) + "\n" + \
                          ("%25s %s" % ("Amount of components:", str(amount)))
                msgbox(message, "Batch details", "OK")

            elif batch_details is True and component_type == "Door Seal Clamp Handle":
                message = ("%25s %s" % ("Batch number:", batch_number)) + "\n" + \
                          ("%25s %s" % ("Location:", location)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", component_type)) + "\n" + \
                          ("%25s %s" % ("Amount of components:", str(amount)))
                msgbox(message, "Batch details", "OK")

            elif batch_details is True and component_type == "Rudder Pivot Pin":
                message = ("%25s %s" % ("Batch number:", batch_number)) + "\n" + \
                          ("%25s %s" % ("Location:", location)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component size:", size)) + "\n" + \
                          ("%25s %s" % ("Amount of components:", str(amount)))
                msgbox(message, "Batch details", "OK")

            # The save_index function is called to save the batch number used after the details are confirmed
            save_index(batch_number)
            data_directory = get_data_directory()

            # Necessary variables are declared here for later use
            component_status = "Manufactured"
            component_finish = "Unfinished"

            # Generate is used instead of amount so that the serial numbers begin at 1 and not 0
            generate = amount + 1
            serial_numbers = []

            # A new batch is created by making an instance of the batch class and passing necessary parameters
            new_batch = Batch(batch_number, amount, serial_numbers, location)

            # This range is used to generate component serial numbers and apply attributes to each class object
            for x in range(1, generate):
                # The current serial is the batch number concatenated with a newly generated unique serial number
                current_serial_number = (str(batch_number) + "-" + str(x).zfill(4))
                # A list of all serial numbers are generated here to be applied to the batch class
                serial_numbers.append(current_serial_number)
                new_component = Component(manufacture_date, component_type, current_serial_number, size,
                                          component_status, component_finish)
                new_component.pick_component(new_batch)

                # Each instance of the component class is stored as a pickle file
                out_file = open(data_directory + new_component.serial + '.pck', 'wb')
                pickle.dump(new_component, out_file)
                out_file.close()

            # This instance of the batch class is stored as a pickle file
            out_file = open(data_directory + new_batch.batch_number + '.pck', 'wb')
            pickle.dump(new_batch, out_file)
            out_file.close()

            # This code is used to generate the message box displaying the status of each component in a batch
            final_message = "Component(s) Status" + "\n" + "-" * 19 + "\n"
            count = len(new_batch.serial_numbers)
            serials_message = ""

            # This code is used to generate a list of component serials and their status for display
            for x in range(0, count):
                current_serial = new_batch.serial_numbers[x]
                current_status = new_batch.batch_status[x]
                status_message = current_serial + ": " + current_status + "\n"
                final_message = final_message + status_message
                serials_message = serials_message + "\n" + current_serial

            # If the user wants to print the above batch details they are printed now
            if batch_details is True:
                serials_list_message = "Component Serial Numbers" + "\n" + "-" * 24 + serials_message
                msgbox(serials_list_message, "Component Serial Numbers", "OK")
                msgbox(final_message, "Component(s) Status", "OK")


# This function is used to generate details about all of the batches in the system
def list_all_batches():

    # Get the "current working directory" to locate the BatchIndex json file
    data_directory = get_data_directory()

    # Open the BatchIndex json file and load the data into the 'json_data' variable
    json_data = get_batch_index()

    if json_data is None or json_data == []:
        msgbox("No batches were found in the system", "List of all batches", "OK")
    else:
        # Necessary variables are declared here before assignment
        amount_of_batches = len(json_data)
        batches = []
        types = []
        sizes = []
        quantities = []
        locations = []

        # Opens the pickle file of each batch
        for x in range(0, amount_of_batches):
            in_file = open(data_directory + json_data[x] + '.pck', 'rb')
            batch_data = pickle.load(in_file)

            # Stores the details of all the files into variable lists for usage later
            batches = batches + [batch_data.batch_number]
            types = types + [batch_data.component_type]
            sizes = sizes + [batch_data.size]
            quantities = quantities + [str(batch_data.amount_components)]
            locations = locations + [batch_data.location]

        # The format of the printed message begins here and is crafted specifically to provide a clean readable output
        # The count variable is used to determine how many batches have been found
        count = len(batches)
        message = "Batch Number" + "\t" + "\t" + "Component Type" + "\t" + "\t" + " "*3 + "Size/Fitment" + "\t" + "\t" + " "*3 + "Location" + "\t" + "\t" + "Quantity"
        table_format = "-"*12 + "\t" + "\t" + "-"*14 + "\t" + "\t" + " "*3 + "-"*12 + "\t" + "\t" + " "*3 + "-"*8 + "\t" + "\t" + "-"*8
        message = message + "\n" + table_format

        # This code is used to generate the output
        for x in range(0, count):
            # This code checks the size of the component size and shortens it for display purposes but doesn't change the stored value
            # For example the size "10mm diamter x 75mm length" is changed to "10mm//75mm" to display the important details
            # If the size is empty "", applies to Door Handle component type, it is changed to N/A to make that clear to the user
            if sizes[x] == "10mm diameter x 75mm length":
                sizes[x] = "10mm//75mm"
            elif sizes[x] == "12mm diameter x 100mm length":
                sizes[x] = "12mm//100mm"
            elif sizes[x] == "16mm diameter x 150mm length":
                sizes[x] = "16mm//150mm"
            elif sizes[x] == "":
                sizes[x] = "N/A"

            # This code checks the size of the component type and shortens it for display purposes but doesn't change the stored value
            # For example the size "Winglet Attachment Strut" is changed to "Winglet Strut" which is still accurate
            if types[x] == "Winglet Attachment Strut":
                types[x] = "Winglet Strut"
            elif types[x] == "Door Seal Clamp Handle":
                types[x] = "Door Handle"
            elif types[x] == "Rudder Pivot Pin":
                types[x] = "Rudder Pin"

            # This code checks if the batch has not been allocated to either the Paisley or Dubai location yet
            if locations[x] == "Factory Floor - Warehouse Not Allocated":
                locations[x] = "-"

            # The details of the batches are concatenated with the display format for output
            new_message = batches[x] + "\t" + "\t" + types[x] + "\t" + "\t" + " "*3 + sizes[x] + "\t" + "\t" + " "*4 + locations[x] + "\t" + "\t" + quantities[x]
            message = message + "\n" + new_message

        msgbox(message, "List of all batches", "OK")


# This function is used to display the details of a batch
def view_batch_details():

    # Get the "current working directory" to locate the BatchIndex json file
    data_directory = get_data_directory()

    # Open the BatchIndex json file and load the data into the 'json_data' variable
    json_data = get_batch_index()
    if json_data is None or json_data == []:
        msgbox("No batches were found in the system", "View batch details", "OK")

    else:
        amount_of_batches = len(json_data)
        batch_data = ""
        batch_number = ""
        check_length = len(batch_number)

        # This loops the input of the batch number until the correct length is input
        while check_length < 12 or check_length > 12:
            batch_number = str(enterbox("Enter batch number in the form YYYYMMDDXXXX", "View details of a batch"))
            check_length = len(batch_number)

            if batch_number == "None":
                check = ynbox("Would you like to return to the menu?", "Cancel view batch details", ["Yes", "No"])
                if check is True:
                    break
            # The code below checks the batch number is the correct length and does not contain letters
            if batch_number != "None":
                if check_length > 12:
                    msgbox("The batch number you entered was too long", "Batch number too long")
                if check_length < 12:
                    msgbox("The batch number you entered was too short", "Batch number too short")
                if batch_number.islower() or batch_number.isupper():
                    msgbox("Batch numbers do not contain any letters", "No letters allowed", "OK")

        # Checks if there are any batch files that match the one input by the user
        for x in range(0, amount_of_batches):
            if json_data[x] == batch_number:
                open_file = batch_number + ".pck"
                in_file = open(data_directory + open_file, 'rb')
                batch_data = pickle.load(in_file)

        # Checks if any batch file was found and loaded into the batch_data variable
        if batch_data != "":
            # This formats the manufacture date into a more readable format without changing the stored value
            formatted_date = batch_data.manufacture_date[0:4] + "-" + batch_data.manufacture_date[4:6] + "-" + batch_data.manufacture_date[6:8]

            # Prints the details of the batch depending on the component type
            if batch_data.component_type == "Winglet Attachment Strut":
                # python for everyone book source
                message = ("%25s %s" % ("Batch number:", batch_data.batch_number)) + "\n" + \
                          ("%25s %s" % ("Location:", batch_data.location)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", batch_data.component_type)) + "\n" + \
                          ("%25s %s" % ("Fitment type:", batch_data.size)) + "\n" + \
                          ("%25s %s" % ("Amount of components:", batch_data.amount_components))
                msgbox(message, "Batch details", "OK")

            elif batch_data.component_type == "Door Seal Clamp Handle":
                message = ("%25s %s" % ("Batch number:", batch_data.batch_number)) + "\n" + \
                          ("%25s %s" % ("Location:", batch_data.location)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", batch_data.component_type)) + "\n" + \
                          ("%25s %s" % ("Amount of components:", batch_data.amount_components))
                msgbox(message, "Batch details", "OK")

            elif batch_data.component_type == "Rudder Pivot Pin":
                message = ("%25s %s" % ("Batch number:", batch_data.batch_number)) + "\n" + \
                          ("%25s %s" % ("Location:", batch_data.location)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", batch_data.component_type)) + "\n" + \
                          ("%25s %s" % ("Component size:", batch_data.size)) + "\n" + \
                          ("%25s %s" % ("Amount of components:", batch_data.amount_components))
                msgbox(message, "Batch details", "OK")

            # This code is used to generate the message box displaying the status of each component in a batch
            final_message = "Component(s) Status" + "\n" + "-"*19 + "\n"
            count = len(batch_data.serial_numbers)
            serials_message = ""

            # Finds a list of serial numbers and status for each component for output
            for x in range(0, count):
                current_serial = batch_data.serial_numbers[x]
                current_status = batch_data.batch_status[x]
                status_message = current_serial + ": " + current_status + "\n"
                final_message = final_message + status_message
                serials_message = serials_message + "\n" + current_serial

            serials_list_message = "Component Serial Numbers" + "\n" + "-"*24 + serials_message
            msgbox(serials_list_message, "Component Serial Numbers", "OK")
            msgbox(final_message, "Component(s) Status", "OK")

        else:
            msgbox("No batch found with that serial number", "No batch found", "OK")


# This function is used to display details of a specific component
def view_component_details():

    # Get the "current working directory" to locate the BatchIndex json file
    data_directory = get_data_directory()
    list_of_files = os.listdir(data_directory)
    # list of files code source (anything with os.)

    serial_number = ""
    check_length = len(serial_number)

    # Open the BatchIndex json file and load the data into the 'json_data' variable
    json_data = get_batch_index()
    if json_data is None or json_data == []:
        msgbox("No components were found in the system", "View component details", "OK")
    else:
        # Loops this code until the correct length is input
        while check_length < 17 or check_length > 17:
            serial_number = str(enterbox("Enter component serial number in the form YYYYMMDDXXXX-XXXX",
                                         "View details of a component"))
            check_length = len(serial_number)

            if serial_number == "None":
                check = ynbox("Would you like to return to the menu?", "Cancel finish component", ["Yes", "No"])
                if check is True:
                    break

            # The code below ensures the serial number input by the user has the correct length, it has a "-" in the right place and is numbers only
            if serial_number != "None":
                if check_length > 17:
                    msgbox("The serial number you entered was too long", "Serial number too long")
                if check_length < 17:
                    msgbox("The serial number you entered was too short", "Serial number too short")
                if serial_number[12:13] != "-":
                    msgbox("Serial number must be the format YYYYMMDDXXXX-XXXX", "Serial number incorrect format")
                if serial_number.islower() or serial_number.isupper():
                    msgbox("Serial numbers do not contain any letters", "No letters allowed", "OK")

        count = len(list_of_files)
        component_data = ""
        component_status = ""

        # Checks if there are any pickle files that match the serial number input by the user
        for x in range(0, count):
            if list_of_files[x][0:17] == serial_number:
                open_file = list_of_files[x]
                in_file = open(data_directory + open_file, 'rb')
                component_data = pickle.load(in_file)
                component_status = component_data.status + "-" + component_data.finish

        if component_data != "":
            formatted_date = component_data.manufacture_date[0:4] + "-" + component_data.manufacture_date[4:6] + "-" + component_data.manufacture_date[6:8]

            # Prints different outputs depending on the component type
            if component_data.component_type == "Winglet Attachment Strut":
                # python for everyone book source
                message = ("%25s %s" % ("Serial number:", component_data.serial)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", component_data.component_type)) + "\n" + \
                          ("%25s %s" % ("Fitment type:", component_data.size)) + "\n" + \
                          ("%25s %s" % ("Current status:", component_status)) + "\n" + \
                          ("%25s %s" % ("Part of batch:", component_data.serial[0:12]))
                msgbox(message, "Component details", "OK")

            elif component_data.component_type == "Door Seal Clamp Handle":
                message = ("%25s %s" % ("Serial number:", component_data.serial)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", component_data.component_type)) + "\n" + \
                          ("%25s %s" % ("Current status:", component_status)) + "\n" + \
                          ("%25s %s" % ("Part of batch:", component_data.serial[0:12]))
                msgbox(message, "Component details", "OK")

            elif component_data.component_type == "Rudder Pivot Pin":
                message = ("%25s %s" % ("Serial number:", component_data.serial)) + "\n" + \
                          ("%25s %s" % ("Manufacture date:", formatted_date)) + "\n" + \
                          ("%25s %s" % ("Component type:", component_data.component_type)) + "\n" + \
                          ("%25s %s" % ("Component size:", component_data.size)) + "\n" + \
                          ("%25s %s" % ("Current status:", component_status)) + "\n" + \
                          ("%25s %s" % ("Part of batch:", component_data.serial[0:12]))
                msgbox(message, "Component details", "OK")

        elif component_data == "" and serial_number != "None":
            msgbox("No component found with that serial number", "No component found", "OK")


# This function is used to allocate a batch of components to either the Paisley or Dubai location
def allocate_manufactured_stock():

    # Get the "current working directory" to locate the BatchIndex json file
    data_directory = get_data_directory()

    # Open the BatchIndex json file and load the data into the 'json_data' variable
    json_data = get_batch_index()
    if json_data is None or json_data == []:
        msgbox("No batches were found in the system", "View batch details", "OK")
    else:
        amount_of_batches = len(json_data)
        not_allocated = False
        batch_data = ""
        batch_number = ""
        check_length = len(batch_number)

        # This code is looped until the batch number input is in the correct format
        while check_length < 12 or check_length > 12:
            batch_number = str(enterbox("Enter batch number in the form YYYYMMDDXXXX", "Allocate manufactured stock"))
            check_length = len(batch_number)

            if batch_number == "None" or batch_number is None:
                check = ynbox("Would you like to return to the menu?", "Cancel view batch details", ["Yes", "No"])
                if check is True:
                    break

            # The below code is used to ensure the batch number input by the user has the correct length and no letters
            if batch_number != "None" and batch_number is not None:
                if check_length > 12:
                    msgbox("The batch number you entered was too long", "Batch number too long")
                if check_length < 12:
                    msgbox("The batch number you entered was too short", "Batch number too short")
                    # islower and isupper source
                if batch_number.islower() or batch_number.isupper():
                    msgbox("Batch numbers do not contain any letters", "No letters allowed", "OK")

        # Checks if there are any batch files that match the number input by the user
        for x in range(0, amount_of_batches):
            if json_data[x] == batch_number:
                open_file = batch_number + ".pck"
                in_file = open(data_directory + open_file, 'rb')
                batch_data = pickle.load(in_file)
                in_file.close()

                # Checks if the batch has already been allocated or if it has the "None" value for insurance
                if batch_data.location == "Factory Floor - Warehouse Not Allocated" or batch_data.location == "None":
                    not_allocated = True

                # If the location is already Paisley or Dubai then it must be allocated already
                elif batch_data.location == "Paisley" or batch_data.location == "Dubai":
                    not_allocated = False
                    msgbox("This batch has already been allocated to the " + batch_data.location + " location",
                           "Batch already allocated", "OK")

        # This variable is declared to store the users choice of location later
        choice = ""

        # If the batch is not empty and hasn't been allocated, this code allows the user to allocate the batch
        if batch_data != "" and not_allocated is True:
            choices = ["Paisley", "Dubai"]

            # Loops until the choice is not empty or not "None", essentially until the user selects Paisley or Dubai or breaks the loop by quitting
            while choice == "" or choice is None or choice == "None":
                choice = choicebox("This batch has not yet been allocated." + "\n" + "\n" + "Select a warehouse to allocate this batch to:", "Select warehouse", choices)
                if choice == "None" or choice is None:
                    check = ynbox("Would you like to return to the menu?", "Cancel view batch details", ["Yes", "No"])
                    if check is True:
                        break

            # If the choice variable is set to a correct choice of Paisley or Dubai, a message is printed
            if choice == "Paisley" or choice == "Dubai":
                batch_data.location = choice
                msgbox("This batch is now allocated and will be shipped to the " + batch_data.location + " location",
                       "Batch allocated", "OK")

                # If a correct choice is made the batch file is opened and stored with the newly allocated location
                open_file = batch_number + ".pck"
                out_file = open(data_directory + open_file, 'wb')
                pickle.dump(batch_data, out_file)
                out_file.close()

        elif batch_data == "" and batch_number != "None":
            msgbox("No batch found with this batch number", "No batch found", "OK")


# This function allows the user to search for specific products
def search_product():

    component_type = ""
    size = ""
    confirm = False

    # Open the BatchIndex json file and load the data into the 'json_data' variable
    json_data = get_batch_index()
    if json_data is None or json_data == []:
        msgbox("No batches were found in the system", "No batches found", "OK")

    else:
        # Loops until the user confirms the details they have input
        while confirm is False:
            # Gets the users choice of component from a choicebox which limits their input to the correct choices only
            component_types = ["Winglet Attachment Strut", "Door Seal Clamp Handle", "Rudder Pivot Pin"]
            component_type = choicebox("Select component type:", "Select component type", component_types)

            if component_type is None:
                check = ynbox("Would you like to return to the menu?", "Cancel product search", ["Yes", "No"])
                if check is True:
                    break

            # Allows the user to input the size of the component they wish to search for where required
            # The user is then asked to confirm those details to proceed or they can re-enter them
            if component_type == "Winglet Attachment Strut":
                sizes = ["A320 Series", "A380 Series"]
                size = choicebox("Select fitment type:", "Fitment type", sizes)
                if size is not None:
                    message = ("%20s %s" % ("Component type:", component_type)) + "\n" + \
                              ("%20s %s" % ("Fitment type:", size))
                    confirm = ynbox("You selected the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    "Are these"
                                    " details correct?", "Confirm selection", ["Yes", "No"])
                    if confirm is None:
                        check = ynbox("Would you like to return to the menu?", "Cancel product search", ["Yes", "No"])
                        if check is True:
                            break
                else:
                    check = ynbox("Would you like to return to the menu?", "Cancel product search", ["Yes", "No"])
                    if check is True:
                        break

            elif component_type == "Door Seal Clamp Handle":
                message = ("%20s %s" % ("Component type:", component_type))
                confirm = ynbox("You selected the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                "Are these details correct?", "Confirm selection", ["Yes", "No"])
                if confirm is None:
                    check = ynbox("Would you like to return to the menu?", "Cancel product search", ["Yes", "No"])
                    if check is True:
                        break

            elif component_type == "Rudder Pivot Pin":
                sizes = ["10mm diameter x 75mm length", "12mm diameter x 100mm length", "16mm diameter x 150mm length"]
                size = choicebox("Select size:", "Select size", sizes)

                if size is not None:
                    message = ("%20s %s" % ("Component type:", component_type)) + "\n" + \
                              ("%20s %s" % ("Component size:", size))
                    confirm = ynbox("You selected the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    "Are these details correct?", "Confirm selection", ["Yes", "No"])
                    if confirm is None:
                        check = ynbox("Would you like to return to the menu?", "Cancel product search", ["Yes", "No"])
                        if check is True:
                            break
                else:
                    check = ynbox("Would you like to return to the menu?", "Cancel product search", ["Yes", "No"])
                    if check is True:
                        break

        # Get the "current working directory" to locate the BatchIndex json file
        # Gets a list of files to search for potential matches and an integer value of how many there are
        data_directory = get_data_directory()
        list_of_files = os.listdir(data_directory)
        amount_of_files = len(list_of_files)

        # These list variables are declared to later store matching details of unfinished components
        unfinished_serials = []
        unfinished_dates = []
        unfinished_dates_formatted = []
        unfinished_finish = []

        # These list variables are declared to later store matching details of finished components
        finished_serials = []
        finished_dates = []
        finished_dates_formatted = []
        finished_finish = []

        # The minimum amount of files that should exist in the Data folder is 3, one for batch, minimum of one component and the BatchIndex.json file
        if amount_of_files > 3:
            for x in range(0, amount_of_files):
                # Searches for files that match the criteria of a component file
                # If a matching file is found, it is loaded into the component_data variable for sorting
                if list_of_files[x][12:13] == "-" and len(list_of_files[x]) == 21:
                    open_file = list_of_files[x]
                    in_file = open(data_directory + open_file, 'rb')
                    component_data = pickle.load(in_file)

                    # Checks if the matching file has the correct component type and size
                    if component_data.component_type == component_type and component_data.size == size:
                        # Checks whether or not the component is unfinished or finished
                        # The code then sorts details of the file such as its serial, date and finish into a list of all of them
                        if component_data.finish == "Unfinished":
                            unfinished_serials = unfinished_serials + [component_data.serial]
                            unfinished_dates = unfinished_dates + [component_data.manufacture_date]
                            unfinished_dates_formatted = unfinished_dates_formatted + [component_data.manufacture_date[0:4] + "-" + component_data.manufacture_date[4:6] + "-" + component_data.manufacture_date[6:8]]
                            unfinished_finish = unfinished_finish + [component_data.finish]
                        else:
                            finished_serials = finished_serials + [component_data.serial]
                            finished_dates = finished_dates + [component_data.manufacture_date]
                            finished_dates_formatted = finished_dates_formatted + [component_data.manufacture_date[0:4] + "-" + component_data.manufacture_date[4:6] + "-" + component_data.manufacture_date[6:8]]
                            finished_finish = finished_finish + [component_data.finish]

        # These variables are used to store the location of unfinished and finished components in lists
        unfinished_locations = []
        finished_locations = []

        total_unfinished = len(unfinished_serials)
        total_finished = len(finished_serials)

        # If the program has found unfinished components, it will attempt to find the matching batch file to get the components location
        # This is kept separate from the code above as the location of a component isn't stored in the component class but only the batch class
        if total_unfinished > 0:
            for x in range(0, total_unfinished):
                open_file = unfinished_serials[x][0:12] + '.pck'
                in_file = open(data_directory + open_file, 'rb')
                batch_data = pickle.load(in_file)

                # If the matching location is found, it is added to the variable list established earlier
                if unfinished_serials[x][0:12] == batch_data.batch_number:
                    unfinished_locations = unfinished_locations + [batch_data.location]

        # If the program has found unfinished components, it will attempt to find the matching batch file to get the components location
        # This is kept separate from the code above as the location of a component isn't stored in the component class but only the batch class
        if total_finished > 0:
            for x in range(0, total_finished):
                open_file = finished_serials[x][0:12] + '.pck'
                in_file = open(data_directory + open_file, 'rb')
                batch_data = pickle.load(in_file)

                # If the matching location is found, it is added to the variable list established earlier
                if finished_serials[x][0:12] == batch_data.batch_number:
                    finished_locations = finished_locations + [batch_data.location]

        # This code is used to print the details of matching products if any are found
        if total_unfinished > 0:
            # The message output to the user is different depending on the component type
            if component_type != "Door Seal Clamp Handle":
                message = "Unfinished Products" + "\n" + "-"*19 + "\n" + "\n" + 'The following "' + size + '" ' + \
                          component_type + "(s), are currently available in stock:" + "\n" + "\n" + "\n" + \
                          "Component Serial#" + "\t" + "\t" + "\t" + "Location" + "\t" + "\t" + "Finish" + "\t" \
                          + "\t" + "Date"
            else:
                message = "Unfinished Products" + "\n" + "-" * 19 + "\n" + "\n" + "The following " + component_type + \
                          "(s), are currently available in stock:" + "\n" + "\n" + "\n" + "Component Serial#" + "\t" \
                          + "\t" + "\t" + "Location" + "\t" + "\t" + "Finish" + "\t" + "\t" + "Date"
            table_format = "-" * 17 + "\t" + "\t" + "\t" + "-" * 8 + "\t" + "\t" + "-" * 6 + "\t" + "\t" + "-" * 4
            message = message + "\n" + table_format
            for x in range(0, total_unfinished):
                # This code checks if the default location of the component is true and changes it to display better
                if unfinished_locations[x] == "Factory Floor - Warehouse Not Allocated":
                    unfinished_locations[x] = "Unallocated"
                # The final message is concatenated with the "table format" and the details and output in a msgbox
                new_message = unfinished_serials[x] + "\t" + "\t" + "\t" + unfinished_locations[x] + "\t" + "\t" + unfinished_finish[x] + "\t" + "\t" + unfinished_dates_formatted[x]
                message = message + "\n" + new_message
            msgbox(message, "Unfinished Products", "OK")

        # The same applies here as above but for finished components
        if total_finished > 0:
            if component_type != "Door Seal Clamp Handle":
                message = "Finished Products" + "\n" + "-"*17 + "\n" + "\n" + 'The following "' + size + '" ' + \
                          component_type + "(s), are currently available in stock:" + "\n" + "\n" + "\n" + \
                          "Component Serial#" + "\t" + "\t" + "\t" + "Location" + "\t" + "\t" + "Finish" + "\t" \
                          + "\t" + "Date"
            else:
                message = "Finished Products" + "\n" + "-" * 17 + "\n" + "\n" + "The following " + component_type + \
                          "(s), are currently available in stock:" + "\n" + "\n" + "\n" + "Component Serial#" + "\t" \
                          + "\t" + "\t" + "Location" + "\t" + "\t" + "Finish" + "\t" + "\t" + "Date"
            table_format = "-" * 17 + "\t" + "\t" + "\t" + "-" * 8 + "\t" + "\t" + "-" * 6 + "\t" + "\t" + "-" * 4
            message = message + "\n" + table_format
            for x in range(0, total_finished):
                if finished_locations[x] == "Factory Floor - Warehouse Not Allocated":
                    finished_locations[x] = "Unallocated"
                new_message = finished_serials[x] + "\t" + "\t" + "\t" + finished_locations[x] + "\t" + "\t" + finished_finish[x] + "\t" + "\t" + finished_dates_formatted[x]
                message = message + "\n" + new_message
            msgbox(message, "Finished Products", "OK")

        # If no matching components are found to the users input then a message is displayed
        if total_finished < 1 and total_unfinished < 1 and component_type is not None:
            msgbox("No stock available with those requirements", "No stock available", "OK")


# This function is used to allow the user to select an appropriate finish for each individual component
def finish_component():

    serial_number = ""
    check_length = len(serial_number)

    # Open the BatchIndex json file and load the data into the 'json_data' variable
    json_data = get_batch_index()
    if json_data is None or json_data == []:
        msgbox("No components were found in the system", "No components found", "OK")

    else:
        # This code is looped until the correct length of serial number is input
        while check_length < 17 or check_length > 17:
            serial_number = str(enterbox("Enter component serial number in the form YYYYMMDDXXXX-XXXX",
                                         "Finish a component"))
            check_length = len(serial_number)

            if serial_number == "None":
                check = ynbox("Would you like to return to the menu?", "Cancel finish component", ["Yes", "No"])
                if check is True:
                    break

            # The code below ensures the serial number input by the user is the correct length, has "-" in the correct place and has no letters
            if serial_number != "None":
                if check_length > 17:
                    msgbox("The serial number you entered was too long", "Serial number too long")
                if check_length < 17:
                    msgbox("The serial number you entered was too short", "Serial number too short")
                if serial_number[12:13] != "-":
                    msgbox("Serial number must be the format YYYYMMDDXXXX-XXXX", "Serial number incorrect format")
                if serial_number.islower() or serial_number.isupper():
                    msgbox("Serial numbers do not contain any letters","No letters allowed", "OK")

        # Get the "current working directory" to locate the BatchIndex json file
        data_directory = get_data_directory()
        list_of_files = os.listdir(data_directory)
        amount_of_files = len(list_of_files)
        confirm = False

        # The minimum amount of files in the Data directory should be 3, one for batch, minimum of one component and the BatchIndex.json file
        if amount_of_files > 3:
            # The code below checks if there are any pickle files that match the serial number input by the user
            for x in range(0, amount_of_files):
                # If a matching file is found, it is opened and loaded into the component_data variable
                if list_of_files[x] == serial_number + '.pck':
                    open_file = list_of_files[x]
                    in_file = open(data_directory + open_file, 'rb')
                    component_data = pickle.load(in_file)
                    in_file.close()

                    # This code looks for the components matching batch file
                    open_file = list_of_files[x][0:12] + '.pck'
                    in_file = open(data_directory + open_file, 'rb')
                    batch_data = pickle.load(in_file)
                    batch_index = batch_data.serial_numbers.index(serial_number)
                    in_file.close()

                    # Checks if a component was found and that it doesn't already have a finish
                    if component_data != "" and component_data.finish == "Unfinished":
                        # This code is looped until the user confirms the details
                        while confirm is not True:

                            # Prints the details differently depending on the component type and asks the user to confirm their selection
                            if component_data.component_type == "Winglet Attachment Strut":
                                message = ("%20s %s" % ("Component type:", component_data.component_type)) + "\n" + \
                                          ("%20s %s" % ("Fitment type:", component_data.size)) + "\n" + \
                                          ("%20s %s" % ("Location:", batch_data.location))
                                confirm = ynbox(
                                    "This component has the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    "Are these component details correct?", "Confirm selection", ["Yes", "No"])
                            elif component_data.component_type == "Door Seal Clamp Handle":
                                message = ("%20s %s" % ("Component type:", component_data.component_type)) + "\n" + \
                                          ("%20s %s" % ("Location:", batch_data.location))
                                confirm = ynbox(
                                    "This component has the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    "Are these component details correct?", "Confirm selection", ["Yes", "No"])
                            elif component_data.component_type == "Rudder Pivot Pin":
                                message = ("%20s %s" % ("Component type:", component_data.component_type)) + "\n" + \
                                          ("%20s %s" % ("Component size:", component_data.size)) + "\n" + \
                                          ("%20s %s" % ("Location:", batch_data.location))
                                confirm = ynbox(
                                    "This component has the following details:" + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    message + "\n" + "\n" + "-" * 50 + "\n" + "\n" +
                                    "Are these component details correct?", "Confirm selection", ["Yes", "No"])

                            if confirm is False:
                                check = ynbox("Would you like to return to the menu?", "Cancel finish component", ["Yes", "No"])
                                if check is True:
                                    break
                    # If a component was found but is already has a finish, the user is notified and returned to the menu
                    elif component_data != "" and component_data.finish != "Unfinished":
                        msgbox("The component " + serial_number + " has already been finished with " + component_data.finish,
                               "Component already finished", "OK")

                    # paint_code and finish are established to get the users input later
                    paint_code = ""
                    finish = ""

                    # Checks that a component was found, it is not finished and that the user confirmed their input details
                    if confirm is True and component_data != "" and component_data.finish == "Unfinished":

                        # Loops this code while the finish variable is empty
                        # Essentially loops this code until a correctly formatted finish is created and applied to the variable
                        while finish == "":

                            # The two finish choices are input via a choicebox which limits the input to the correct choices
                            choices = ["Polished", "Painted"]
                            choice = choicebox("Select finish for component " + serial_number, "Select a finish", choices)

                            if choice is None:
                                check = ynbox("Would you like to return to the menu?", "Cancel finish component",
                                              ["Yes", "No"])
                                if check is True:
                                    break
                            # If the users choice is "Polished" then the finish is set to "Polished"
                            if choice == "Polished":
                                finish = "Polished"

                            # If the users choice is "Painted" then more input and validation is required
                            if choice == "Painted":
                                code_format = False
                                # Loops this code while the paint_code is empty/None, also while the length and format are incorrect
                                while paint_code == "None" or len(paint_code) != 4 or paint_code == "" or code_format is False:
                                    code_format = False
                                    check_letters = 0
                                    check_numbers = 0
                                    # Asks the user to input a paint_code in the appropriate format
                                    paint_code = str(enterbox("Please enter a 4 character paint code in the form AAXX where AA are two letters and XX are two numbers",
                                                              "Paint code"))

                                    if paint_code == "None" or paint_code is None:
                                        check = ynbox("Would you like to return to the menu?", "Cancel finish component",
                                                      ["Yes", "No"])
                                        if check is True:
                                            break

                                    # The code below is used to check that the paint_code has the correct length and format
                                    if paint_code != "None" or paint_code is not None:
                                        if len(paint_code) < 4:
                                            msgbox("The paint code you entered was too short", "Paint code too short")
                                        if len(paint_code) > 4:
                                            msgbox("The paint code you entered was too long", "Paint code too long")
                                        if len(paint_code) == 4:

                                            # Checks if the first two characters are letters
                                            for x in range(0, 2):
                                                # Checks if the first two characters are letters
                                                if paint_code[x].isupper() or paint_code[x].islower():
                                                    check_letters = check_letters
                                                else:
                                                    check_letters = check_letters + 1

                                            # Checks if the last two characters are numbers
                                            for xa in range(2, 4):
                                                try:
                                                    int(paint_code[xa])
                                                    check_numbers = check_numbers
                                                except ValueError:
                                                    check_numbers = check_numbers + 1

                                            # If any errors are found from checking the character, the user is notified
                                            if check_letters > 0:
                                                msgbox("The first two characters in the code should be letters",
                                                       "Incorrect code format", "OK")
                                            if check_numbers > 0:
                                                msgbox("The last two characters in the code should be numbers",
                                                       "Incorrect code format", "OK")

                                            # If no errors are found then the paint_code variable is assigned
                                            if check_letters == 0 and check_numbers == 0:
                                                code_format = True
                                                paint_code = paint_code[0:2].upper() + paint_code[2:]

                                    # If the correct format and length are input the finish variable adpots the paint_code value and concatenates it with "Paint:"
                                    if code_format is True and len(paint_code) == 4 and paint_code != "None" and paint_code is not None:
                                        finish = "Paint:" + paint_code

                            # If a correct input for the finish is input the following code applies
                            if finish == "Polished" or finish[0:6] == "Paint:":

                                # The component_data and batch_data variables and files are updated with the correct data
                                component_data.finish = finish
                                batch_data.batch_status[batch_index] = "Manufactured" + "-" + finish
                                msgbox("Component " + serial_number + " will be finished using " + finish,
                                       "Finish Confirmed", "OK")

                                # Opens the component file and saves it with the updated component data
                                open_file = serial_number + '.pck'
                                out_file = open(data_directory + open_file, 'wb')
                                pickle.dump(component_data, out_file)
                                out_file.close()

                                # Opens the matching batch file and saves it with the updated batch data
                                open_file = serial_number[0:12] + '.pck'
                                out_file = open(data_directory + open_file, 'wb')
                                pickle.dump(batch_data, out_file)
                                out_file.close()
        else:
            msgbox("No components found in the system", "No components found", "OK")


# this function acts as the main menu for the program
def main():

    # The message and title of the menu are declared here
    msg = "Welcome to the PPEC Inventory System menu" + "\n" + "-"*41 + "\n" + "\n" + "Choose an option to begin: "
    title = "PPEC Inventory System"

    # The choice and available menu choices are declared here
    choice = ""
    choices = ["Create a new batch", "List all batches", "View details of a batch", "View details of a component",
               "Allocate manufactured stock", "Search by product type", "Finish a component", "Quit"]

    # Loops the menu until the user decides to quit the program
    while choice != "Quit":

        # This code acts as the menu specifically, the parameters are declared above and this code gets the users choice
        choice = choicebox(msg, title, choices)

        # This if statement is used to determine the functionality of the list
        # It checks which meny choice the user makes and performs the attributed code, usually calling a function
        if choice == "Create a new batch":
            create_batch()
        elif choice == "List all batches":
            list_all_batches()
        elif choice == "View details of a batch":
            view_batch_details()
        elif choice == "View details of a component":
            view_component_details()
        elif choice == "Allocate manufactured stock":
            allocate_manufactured_stock()
        elif choice == "Search by product type":
            search_product()
        elif choice == "Finish a component":
            finish_component()

        # Checks If the users choice is "Quit" or if "choice is None", which means cancel or the closing the box
        # If either of the above are the case then the program is quit
        elif choice == "Quit":
            msgbox("You have chosen to exit the program", "Goodbye", "OK")
            sys.exit(0)
        elif choice is None:
            msgbox("You have chosen to exit the program", "Goodbye", "OK")
            sys.exit(0)


# This is the code that calls the main() function which essentially starts the program and code
if __name__ == '__main__':
    main()

