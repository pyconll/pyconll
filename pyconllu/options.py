################################################################################
#
# A class to handle different command line options in a program. Add the options
# you want to detect and a description if desired. Then pass in the command line
# arguments from the program to parse. You will then be able to get request if
# a given field was in the command line arguments given the field.
#
# You provide a dictionary of tuples for version of a command line option along
# with a meta prefix for the method meta_present.
#
################################################################################
class OptionsProcessor(object):
    def __init__(self):
        self.options = {}
        self.processed = {}

    # Adds the given option with the meta name provided. Option is assumed
    # to be an iterable type, even if it only has one element. This way there
    # can be multiple versions of the same option. This meta name is what will
    # prefix a method name to find out if the option was present.
    def add_option(self, option, meta=''):
        self.options[option] = meta
        if meta:
            setattr(self, meta + '_present', lambda: self.present(option))

    # Process the given arguments, and update the internal state. For any call
    # to *_present methods, it is referring to the results of the last process
    # call. Note, that args should be in a list format as given by sys.argv.
    def process(self, args):
        for option, _ in self.options.items():
            p = reduce(lambda found, arg: found or arg in option, args, False)
            self.processed[option] = p

    def present(self, option):
        return self.processed[option]
