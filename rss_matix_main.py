from tkinter_view import windows as view
from controller import Controller
from model import model
import os
from Check_dependencies import check_dependencies

# Import the logger function
from model_package.logging_setup import setup_logger

# Create a logger object
logger = setup_logger(__name__)

# Logs where the current directory is
logger.info(f"'Get current working directory : ', {os.getcwd()}")

# Import the model, controller and view


if __name__ == "__main__":
    try:
        # Checks if all third-party dependencies are installed (see: requirements.txt)
        check_dependencies()

        # Creates the model object
        model_obj = model()

        # Creates the controller object and starts the mainloop for the view
        app_obj = Controller(view, model_obj)
        app_obj.start_mainloop()

    except Exception as e:
        logger.exception(e)
        logger.error('Something went horribly wrong, please restart the program.\
                     We are sending a group of trained monkeys to fix the problem.')
