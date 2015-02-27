__author__ = 'faiz'

from flanker_test import Cognitives
from stroop_test import StroopTest
from sart_test import SartTest
import sys
import getopt


def main(argv):

    test = None

    try:
        opts, operands = getopt.getopt(sys.argv[1:], 't:', ["test="])

        if len(sys.argv) < 2:
            print 'Not enough argument!'
            sys.exit()
        else:
            for option, value in opts:
                if option == "-t" or option == "--test":
                    if int(value) == 1 or int(value) == 2 or int(value) == 3:
                        test = value
                    else:
                        print 'Invalid argument: %s' % value
                        sys.exit()

    except getopt.GetoptError, err:
        print str(err)

    app = Cognitives(int(test))
    app.run()

if __name__ == '__main__':
    main(sys.argv)