__author__ = 'fpombeiro'
import email_module as ee
import time
import sys, os


if __name__ == '__main__':
    try:
        start = time.time()
        ee.send_email()
        end = time.time()
        
        print("Successfully ran program in {time_spent} minutes".format(
                                        time_spent=str(round((end-start)/60,2))))
    except Exception as e:
        print("email failed to send just now due to ", e)


