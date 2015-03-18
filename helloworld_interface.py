from cmd2 import Cmd, make_option, options
import readline
import optparse


class HelloWorld(Cmd):
    """Simple command processor example."""

    FRIENDS = ['Alice', 'Adam', 'Barbara', 'Bob']

    @options([make_option('-p', '--piglatin', action="store_true", help="atinLay"),
                          make_option('-s', '--shout', action="store_true", help="N00B EMULATION MODE"),
                          make_option('-r', '--repeat', type="int", help="output [n] times")
                         ])
    def do_greet(self, person, opts=None):
        "Greet the person"
        print opts
        # sauce = self.select(['90', '180', '360'], 'Select number of samples:')
        # if person and person in self.FRIENDS:
        #     greeting = 'hi, %s!' % person
        # elif person:
        #     greeting = "hello, " + person
        # else:
        #     readline.parse_and_bind("tab: complete")
        #     completer = self.Completer(self.FRIENDS)
        #     readline.set_completer(completer.complete)
        #     person2 = raw_input('Enter friend name: ')
        #     greeting = 'hello, ' + person2
        # print greeting
        completer = self.Completer(self.FRIENDS)
        readline.set_completer(completer.complete)
        person2 = raw_input('Enter friend name: ')
        ans = self.select('yes no', 'redo?')
        if ans == 'yes':
            print self.colorize('juan', 'bold')
            self.do_greet('-p juan')

    def complete_greet(self, text, line, begidx, endidx):
        if not text:
            completions = self.FRIENDS[:]
        else:
            completions = [f
                            for f in self.FRIENDS
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

if __name__ == '__main__':
    HelloWorld().cmdloop()