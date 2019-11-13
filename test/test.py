from ailab.webap_tools.auto_punch import AutoPunching
import time

test_ap = AutoPunching("cbc106008", "2848444B")


def procedure_while_test():
    while True:
        test_ap.nav_to_checkform()
        time.sleep(3)
        test_ap.fill_break_time()
        time.sleep(1)
        test_ap.logout()
        time.sleep(5)


if __name__ == '__main__':

    procedure_while_test()
