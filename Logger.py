# Using our STEM_EDX_Pipeline logging code
import logging

class log():
    """
    Type: Create a log file to record information about processes and errors.
    Explanation: This class provides methods to write information and errors to a 
                 log file.
    Attributes: 1. logger: The logger object for recording information and errors.
    """
    def __init__(self, log_name):
        """
        Input: 1. log_name (str): The name of the log file.
        Explanation: Initialize the log object.
        """
        # Set the logging level to suppress font management messages
        logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)

        # Make the logger basic configuration
        logging.basicConfig(filename=log_name, 
                    format='%(asctime)s %(message)s',
                    filemode='w')

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

    def write_to_logger(self, text):
        """
        Input: 1. text (str): The information to be recorded.
        Explanation: Write information to the log file.
        """
        self.logger.info(text)

    def error_to_logger(self, text):
        """
        Input: 1. text (str): The error message to be recorded.
        Explanation: Write an error message to the log file.
        """
        self.logger.error(text)