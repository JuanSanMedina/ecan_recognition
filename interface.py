import time
import readline
import cmd2
import requests
from termcolor import colored
import socket

hostname = socket.gethostname()
if hostname == 'CUSP-raspberrypi':
    import weight
    import RPi.GPIO as GPIO
    import set_stepper as stepper
    import upload_functions as uf


class ecan_interface(cmd2.Cmd):
    """Ecan Command Line Interface Application."""

    # Set GPIOs and url
    url = 'http://128.122.72.105:8000'
    # url = 'http://127.0.0.1:8000'

    # Class variables
    ATT_KEYS = ['logo', 'shape', 'material', 'common_name']
    ATT_DICT = dict.fromkeys(ATT_KEYS)

    # Update ATT_DICT
    for k in ATT_KEYS:
        data = {'action': 'view', 'att_key': k}
        d = requests.post(url + '/ecan/insert/', data).json()
        ATT_DICT[k] = eval(d['dictionary'])

    # Uploaded items in session
    UP_IT = {}

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

        while True:
            self.upload_insert(arg=arg)
            color_arg = colored(arg, 'blue', attrs=['bold'])
            ans = self.select(['yes', 'no'],
                              'Add other %s?: ' % color_arg)
            if ans == 'no':
                break
                return

    def do_upload(self, arg):
        """Data collection function
        Gets no arguments neither options
        """
        # Start process
        while True:
            # Initialize item dictionary
            keys = ['weight', 'identifier', 'common_name', 'shape',
                    'material', 'logo', 'transparency']
            item_att = dict.fromkeys(keys)

            # Take preview of object
            # Previews are available at api/site_media/media/sample
            ans = self.select(['yes', 'no'], "Take preview?: ")
            if ans == 'yes':
                self.do_take_preview()

            # Get attributes
            for k in self.ATT_KEYS:
                item_att[k] = self.get_attributes(k)

            # Ask for transparency
            item_att['transparency'] = \
                self.select(['yes', 'no'], "Is it transparent?: ")

            # Run data collection
            while True:
                # Check if gram scale and collect weight
                item_att['weight'] = self.do_get_weight('return')

                # Select number of samples
                samples = self.select(['90', '180', '360'],
                                      'Select number of samples: ')

                # Set item identifier
                item_att['identifier'] = '%.2f' % time.time()

                # Confirm data package
                print '\nData package:'
                print item_att
                print 'Number of samples %s\n' % samples
                attention = colored('Atention! ', 'yellow', attrs=['bold'])
                ans = self.select(['yes', 'no'],
                                  attention + 'Confirm data-package?: ')
                if ans == 'yes':
                    result = uf.get_data(int(samples), item_att, self.url)
                    self.UP_IT[item_att['identifier']] = 1
                    print result

                # Run with same data_package?
                ans = self.select(['yes', 'no'],
                                  'Run again with same attributes?: ')
                if ans == 'no':
                    break

            # Continue data collection?
            ans = self.select(['yes', 'no'], 'Continue data collection?: ')
            if ans == 'yes':
                pass
            else:
                readline.set_completer(self.complete)
                break

    def do_take_preview(self, arg=None):
        """Run to take an ecan preview"""
        while True:
            ans = self.select(['yes', 'no'], "Take?: ")
            if ans == 'yes':
                uf.get_preview(self.url)
            elif ans == 'no':
                break

    def do_delete_object(self, arg=None):
        """Run to take an ecan preview"""
        if arg:
            data = {'identifier': arg}
            r = requests.get(self.url + '/ecan/delete_object/',
                             params=data)
            print r.json()['result']
        else:
            while True:
                identifier = self.select(self.UP_IT.keys(),
                                         "Select object to delete: ")
                ans = self.select(['yes', 'no'], "Continue?: ")
                if ans == 'yes':
                    data = {'identifier': identifier}
                    r = requests.get(self.url + '/ecan/delete_object/',
                                     params=data)
                    print r.json()['result']
                elif ans == 'no':
                    break

    def upload_insert(self, arg):
        # Ask for new value
        while True:
            ans = raw_input('\nEnter %s: ' % arg).lower().replace(' ', '_')
            cont = self.select(['yes', 'no'],
                               "Proceed?: ")
            if cont == 'yes' and ans not in self.ATT_DICT[arg].keys():
                break
            elif cont == 'no':
                return
            elif ans not in self.ATT_DICT[arg].keys():
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

    def do_get_weight(self, arg=None):
        while True:
            try:
                w = weight.get()
                print '\nCurrent weight %s:' % \
                    colored(w, 'blue', attrs=['bold'])
                ans = self.select(['yes', 'no'],
                                  "does this weight make sense?: ")
                if ans == 'yes':
                    if arg is None:
                        return
                    if arg is 'return':
                        return w
                    break
            except AttributeError:
                print "Please connect and turn on the scale"
                ans = self.select(['yes', 'no'],
                                  "ready?: ")
                if ans == 'no':
                    break

    def get_attributes(self, k):
        print '\nInsert %s:' % colored(k, 'blue', attrs=['bold'])

        while True:
            completer = self.Completer(['1', '2', '3'])
            readline.set_completer(completer.complete)
            ans = self.select(['View existing',
                               'Insert new', 'Insert existing'],
                              'Please select one option: ')

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
                    # cont = self.select(['yes', 'no'], "Continue?: ")
                    # if cont == 'yes' and ans in self.ATT_DICT[k].keys():
                    if ans in self.ATT_DICT[k].keys():
                        value = self.ATT_DICT[k][ans]
                        break
                    else:
                        print colored('Error: ', 'red') + \
                            'please insert a valid %s' % k

                print '\n%s: %s succesfully added' % \
                    (colored('Valid', 'green'), k)
                break
        return value

    def update_attributes(self):
            """Update database attributes"""
            for k in self.ATT_KEYS:
                data = {'action': 'view', 'att_key': k}
                d = requests.post(self.url + '/ecan/insert/', data).json()
                self.ATT_DICT[k] = eval(d['dictionary'])

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
                        return word
                    else:
                        state -= 1

    def do_EOF(self, line):
        return True

    def select(self, options, prompt='Your choice? '):
        """Presents a numbered menu to the user.  Modelled after
           the bash shell's SELECT.  Returns the item chosen.

           Argument ``options`` can be:

             | a single string -> will be split into one-word options
             | a list of strings -> will be offered as options
             | a list of tuples -> interpreted as (value, text), so
                                   that the return value can differ from
                                   the text advertised to the user """
        if isinstance(options, basestring):
            options = zip(options.split(), options.split())
        fulloptions = []
        for opt in options:
            if isinstance(opt, basestring):
                fulloptions.append((opt, opt))
            else:
                try:
                    fulloptions.append((opt[0], opt[1]))
                except IndexError:
                    fulloptions.append((opt[0], opt[0]))
        flag = True
        for (idx, (value, text)) in enumerate(fulloptions):
            if flag:
                self.poutput('\n  %2d. %s\n' % (idx+1, text))
                flag = False
            else:
                self.poutput('  %2d. %s\n' % (idx+1, text))
        while True:
            response = raw_input(prompt)
            try:
                response = int(response)
                result = fulloptions[response - 1][0]
                break
            except ValueError:
                pass # loop and ask again
        return result

if __name__ == '__main__':
    if hostname == 'CUSP-raspberrypi':
        stepper.set_gpio()

    ecan_interface().cmdloop()

    if hostname == 'CUSP-raspberrypi':
        GPIO.cleanup()
