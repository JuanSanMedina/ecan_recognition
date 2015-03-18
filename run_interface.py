import socket
if socket.gethostname() == 'CUSP-raspberrypi':
    import get_weight
    import RPi.GPIO as GPIO
    import set_stepper as stepper
    from upload_functions import *

import time
import readline
import cmd2
import requests
from termcolor import colored


class ecan_interface(cmd2.Cmd):
    """Ecan Command Line Interface Application."""

    # Class variables
    ATT_KEYS = ['logo', 'shape', 'material', 'common_name']
    ATT_DICT = dict.fromkeys(ATT_KEYS)

    def update_attributes(self):
        """Update database attributes"""
        for k in self.ATT_KEYS:
            data = {'action': 'view', 'att_key': k}
            d = requests.post(self.url + '/ecan/insert/', data).json()
            self.ATT_DICT[k] = eval(d['dictionary'])

    # Set GPIOs and url
    url = 'http://128.122.72.105:8000'
    # url = 'http://127.0.0.1:8000'

    # Update ATT_DICT
    update_attributes()

    @cmd2.options([cmd2.make_option('-v', '--view',
                                    action="store_true",
                                    help="view current values and exit")])
    def do_insert(self, arg, opts=None):
        """Insert a new item attribute to database
        Keyword arguments:
        logo -- add new logo (default 0.0)
        shape -- add new shape (default 0.0)
        material -- add new material (default 0.0)
        """
        if not arg or arg not in self.ATT_KEYS:
            print colored('Error: ', 'red') + \
                'please insert a valid argument [help insert]'
            return

        self.update_attributes()
        values_print = [colored(e, 'blue', attrs=['bold'])
                        for e in self.ATT_DICT[arg].keys()]

        if opts.view:
            print '\t'.join(str(e) for e in values_print)
            return

        print '\nCurrent %ss:' % arg
        print '\t'.join(str(e) for e in values_print)

        self.upload_insert(arg=arg)

    def do_upload(self):
        """Data collection function
        Gets no arguments neither options
        """
        # Start process
        while True:
            # Initialize item dictionary
            keys = ['weight', 'identifier', 'common_name', 'shape',
                    'material', 'logo', 'transparency']
            item_att = dict.fromkeys(keys)

            # Check if gram scale and collect weight
            item_att['weight'] = self.weight()

            # Take preview of object
            # Previews are available at api/site_media/media/sample
            ans = self.select(['yes', 'no'], "Take preview?")
            if ans == 'yes':
                self.do_take_preview()

            # Get attributes
            for k in self.ATT_KEYS:
                item_att[k] = self.get_attributes(k)

            # Ask for transparency
            item_att['transparency'] = \
                self.select(['yes', 'no'], "Is transparent?")

            # Run data collection
            while True:
                # Select number of samples
                samples = self.select(['90', '180', '360'],
                    'Select number of samples:')

                # Set item identifier
                item_att['identifier'] = time.time()
                print item_att, samples
                # result = get_data(int(samples), item_att, url)
                # print result
                ans = self.select(['yes', 'no'],
                                  'Run again with same attributes?')
                if ans == 'no':
                    break

            # Continue data collection?
            ans = self.select(['yes', 'no'], 'Continue data collection?')
            if ans == 'yes':
                pass
            else:
                readline.set_completer(self.complete)
                break

    def do_take_preview(self):
        """Run to take an ecan preview"""
        while True:
            take = self.select(['yes', 'no'], "Take?")
            if take == 'yes':
                print 'uncomment get preview'
                # get_preview(self.url)
            ans = self.select(['yes', 'no'], "Keep taking?")
            if ans == 'no':
                break

    def upload_insert(self, arg):
        # Ask for new value
        while True:
            ans = raw_input('Enter %s:' % arg).lower().replace(' ', '_')
            cont = self.select(['yes', 'no'],
                               "Continue?")
            if cont == 'yes' and ans not in self.ATT_DICT[arg].keys():
                break
            else:
                print arg + ' already exists'

        # Upload new attribute
        data = {'att_key': arg, 'action': 'save', 'value': ans}
        r = requests.post(self.url + '/ecan/insert/', data=data).json()
        d = eval(r['dictionary'])
        print '*** %s: succesfully added*** ' \
            % colored(r['result'], 'green')
        self.ATT_DICT[arg][ans] = d[ans]
        print '\nUpdated %ss: ' % arg
        print '\t'.join(colored(e, 'green',
                                attrs=['bold']) for e in d.keys())

    def weight(self):
        while True:
            try:
                # w = get_weight.get()
                w = 10
                print '\nCurrent weight %s:' % \
                    colored(w, 'blue', attrs=['bold'])
                ans = self.select(['yes', 'no'],
                                  "does this weight make sense?")
                if ans == 'yes':
                    break
            except 'NoneType':
                print "Please connect and turn on the scale"
        return w

    def get_attributes(self, k):
        print '\nInsert %s:' % colored(k, 'blue', attrs=['bold'])

        while True:
            completer = self.Completer(['1', '2', '3'])
            readline.set_completer(completer.complete)
            ans = self.select(['View existing',
                               'Insert new', 'Insert existing'],
                              'Please select one option:')

            # View existing
            if ans == 'View existing':
                self.do_insert('-v ' + k)

            # Insert new
            elif ans == 'Insert new':
                self.do_insert(k)

            # Insert existing
            elif ans == 'Insert existing':
                completer = self.Completer(
                    self.ATT_DICT[k].keys())
                readline.set_completer(completer.complete)
                prompt = colored('\n[double tab for options]',
                                 'blue', attrs=['bold']) + '\nInsert %s:' % k

                while True:
                    ans = raw_input(prompt).lower()
                    cont = self.select(['yes', 'no'], "Continue?")
                    if cont == 'yes' and ans not in self.ATT_DICT[k].keys():
                        value = self.ATT_DICT[k][ans]
                        break
                    else:
                        print colored('Error: ', 'red') + \
                            'please insert a valid %s' % k

                print '\n%s: %s succesfully added' % \
                    (colored('Valid', 'green'), k)
                break
        return value

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
