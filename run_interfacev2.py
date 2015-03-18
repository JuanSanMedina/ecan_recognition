# import get_weight
# import RPi.GPIO as GPIO
# import set_stepper as stepper
# from upload_functions import *
import time
import readline
import cmd2
import requests
from termcolor import colored


class ecan_interface(cmd2.Cmd):

    """Ecan Command Line Interface Application."""

    # Set GPIOs and url
    # url = 'http://128.122.72.105:8000'
    url = 'http://127.0.0.1:8000'

    # Class variables
    ATT_KEYS = ['brand', 'shape', 'material', 'description']
    ATT_DICT = dict.fromkeys(ATT_KEYS)

    for k in ATT_KEYS:
        data = {'action': 'view', 'att_key': k}
        d = requests.post(url + '/ecan/insert/', data).json()
        ATT_DICT[k] = eval(d['dictionary'])

    @cmd2.options([cmd2.make_option('-v', '--view',
                                    action="store_true",
                                    help="view current values and exit")])
    def do_insert(self, arg, opts=None):
        """Insert a new item attribute to database
        Keyword arguments:
        brand -- add new brand (default 0.0)
        shape -- add new shape (default 0.0)
        material -- add new material (default 0.0)
        """
        if not arg or arg not in self.ATT_KEYS:
            print colored('Error: ', 'red') + \
                'please insert a valid argument [help insert]'
            return

        objects = self.ATT_DICT[arg].keys()
        values_print = [colored(e, 'blue', attrs=['bold'])
                        for e in objects]

        if opts.view:
            print '\t'.join(str(e) for e in values_print)
            return

        print 'Current %ss:' % arg
        print '\t'.join(str(e) for e in values_print)

        ans = None
        while not ans:
            ans = raw_input('Enter %s:' % arg).lower()

        if ans not in objects:
            data = {'att_key': arg, 'action': 'save', 'value': ans}
            r = requests.post(self.url + '/ecan/insert/', data=data).json()
            d = eval(r['dictionary'])
            print '*** the operation is: %s*** ' \
                % colored(r['result'], 'green')
            self.ATT_DICT[arg][ans] = d[ans]
            print '\nUpdated %ss: ' % arg
            print '\t'.join(colored(e, 'green',
                                    attrs=['bold']) for e in d.keys())
        else:
            print arg + ' already exists'

    def do_upload(self, arg):
        # Start process
        while True:
            # Initialize item dictionary
            keys = ['weight', 'identifier', 'description', 'shape',
                    'material', 'brand', 'transparency']
            item_att = dict.fromkeys(keys)

            # Check if gram scale is connected and/or turned on
            while True:
                try:
                    # w = get_weight.get()
                    w = 10
                    print w
                    ans = self.select(['yes', 'no'],
                                      "does this weight make sense?")
                    if ans == 'yes':
                        item_att['weight'] = w
                        break
                except 'NoneType':
                    print "Please connect and turn on the scale"

            # Take preview of object
            # Previews are available at api/site_media/media/sample
            ans = self.select(['yes', 'no'], "Take preview?")
            if ans == 'yes':
                while ans == 'yes':
                    take = self.select(['yes', 'no'], "Take?")
                    if take == 'yes':
                        print 'uncomment get preview'
                        # get_preview(self.url)
                    ans = self.select(['yes', 'no'], "Keep taking?")

            # Collect data
            samples = self.select(['90', '180', '360'],
                                  'Select number of samples:')

            # Get attributes
            for k in self.ATT_KEYS:
                print '\nInsert %s:' % colored(k, 'blue', attrs=['bold'])
                # Get value
                while True:
                     # Set completer
                    completer = self.Completer(
                        self.ATT_DICT[k].keys())
                    readline.set_completer(completer.complete)
                    ans = self.select(['View existing',
                                       'Insert new', 'Insert existing'],
                                      'Please select one option:')
                    if ans == 'View existing':
                        self.do_insert('-v ' + k)
                    elif ans == 'Insert new':
                        self.do_insert(k)
                         # Set completer
                        completer = self.Completer(
                            self.ATT_DICT[k].keys())
                        readline.set_completer(completer.complete)
                    elif ans == 'Insert existing':
                        prompt = '[double tab for options]\
                            \nInsert %s:' % k
                        ans = raw_input(prompt)
                        while ans not in self.ATT_DICT[k].keys():
                            print colored('Error: ', 'red') + \
                                'please insert a valid %s' % k
                            ans = raw_input(prompt)
                        item_att[k] = self.ATT_DICT[k][ans]
                        print '\n%s: %s succesfully added' % \
                            (colored('Valid', 'green'), k)
                        break

            item_att['transparency'] = self.select(
                ['yes', 'no'], "Is transparent?")
            item_att['identifier'] = time.time()
            # result = get_data(int(samples), item_att, url)
            # print result]
            print samples, item_att
            ans = self.select(['yes', 'no'], 'Continue?')
            if ans == 'yes':
                pass
            else:
                readline.set_completer(self.complete)
                break

    def complete_insert(self, text, line, begidx, endidx):
        if not text:
            completions = self.ATT_KEYS
        else:
            completions = [f
                           for f in self.ATT_KEYS
                           if f.startswith(text)
                           ]
        return completions

    class Completer:

        def __init__(self, completions):
            self.completions = completions

        def complete(self, text, state):
            for word in self.completions:
                if word.startswith(text):
                    if not state:
                        # return colored(word, 'blue', attrs=['bold'])
                        return word
                    else:
                        state -= 1

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    # stepper.set_gpio()
    ecan_interface().cmdloop()
    # GPIO.cleanup()
