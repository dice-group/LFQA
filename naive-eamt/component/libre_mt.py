# This class demonstrates how each component should look like
class LibreMt:
    sample_var = None
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        self.sample_var = 'sample content'
        print('SampleComponent class has been initialized.')
    
    
    def process_input(inpt):
        """
        Each class must have process_input function. 
        Depending upon the type of the component, it should expect/verify a certain input format.
        The output should always be formatted as per the requirements as well. 
        The input and output format for different component types can be found in the main readme file.
        """
        print('Sample process_input function has been called. It can make use of: ', sample_var)