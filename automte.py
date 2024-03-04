from random import choice

import pandas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager

working = None
problem_status = None
logs_left = None
completed = None
final_status = None
total_logs = None
logs_completed = None


def check_logs():
    return logs_left, working, problem_status, completed, final_status, total_logs, logs_completed


class Automation:
    def __init__(self):
        self.problem_logins = None
        self.date = None
        self.date2 = None
        self.midweek = None
        self.attendance = None
        self.meeting_list = None
        self.filepath = None
        self.login_dict = None
        self.testimony_list = None
        self.first_timers = None
        self.sunday = None

    def read_csv(self, filepath, meeting_list, testimony_list, attendance1, attendance2, first_timers1,
                 first_timers2, midweek1, midweek2, sunday1, sunday2, date, date2):
        self.filepath = filepath
        self.meeting_list = meeting_list
        self.testimony_list = testimony_list
        self.attendance = list(range(int(attendance1), int(attendance2)))
        self.first_timers = list(range(int(first_timers1), int(first_timers2)))
        self.midweek = list(range(int(midweek1), int(midweek2)))
        self.sunday = list(range(int(sunday1), int(sunday2)))
        self.date = date
        self.date2 = date2

        pd = pandas.read_csv(f'{self.filepath}')
        emails = pd.to_dict()['email']
        passwords = pd.to_dict()['password']
        self.login_dict = {}
        for i in range(len(emails)):
            self.login_dict[i] = {
                'email': emails[i],
                'password': passwords[i]
            }
        global total_logs
        total_logs = len(self.login_dict)

    def begin_automation(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('detach', True)
        chrome_options.add_argument('--remote-debugging-pipe')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        driver.get('https://celfonline.org/V3/index.php?r=Site/Login')
        self.problem_logins = {'email': [], 'password': []}

        for n in range(len(self.login_dict)):
            global working
            working = f'{self.login_dict[n]["email"]}'
            # log in
            email = driver.find_element(By.NAME, 'username')
            email.send_keys(self.login_dict[n]['email'])

            password = driver.find_element(By.NAME, 'password')
            password.send_keys(self.login_dict[n]['password'])
            password.send_keys(Keys.ENTER)

            try:
                cell_report = driver.find_element(By.LINK_TEXT, 'Submit Cell Reports')
            except NoSuchElementException:
                # global problem_status
                problem_status = (f'Problem with {self.login_dict[n]["email"]}. Number {n + 1}/{len(self.login_dict)}. '
                                  f'\nLogging Out...')
                self.problem_logins['email'].append(self.login_dict[n]['email'])
                self.problem_logins['password'].append(self.login_dict[n]['password'])

                df = pandas.DataFrame(self.problem_logins)
                df.to_csv('static/problem_logs.csv')

                try:
                    log_out = driver.find_element(By.LINK_TEXT, 'LOGOUT')
                    log_out.click()
                except NoSuchElementException:
                    try:
                        log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                        log_out.click()
                    except NoSuchElementException:
                        email = driver.find_element(By.NAME, 'username')

            else:
                cell_report.click()

                for i in self.meeting_list:
                    # --------ADDING THE REPORTS---------
                    if i == 'prayerandplanning':
                        try:
                            type_of_meeting = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[1]'
                                                                            '/td[2]/div/div[1]/label/input')
                            type_of_meeting.click()
                        except ElementClickInterceptedException:
                            # -------------Close Pop Up----------------
                            not_necessary = driver.find_element(By.XPATH,
                                                                '//*[@id="onesignal-slidedown-cancel-button"]')
                            not_necessary.click()
                            # -------------Close Pop Up----------------
                            type_of_meeting = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[1]'
                                                                            '/td[2]/div/div[1]/label/input')
                            type_of_meeting.click()
                        except NoSuchElementException:
                            global problem_status
                            problem_status = (f'Problem with {self.login_dict[n]["email"]}. '
                                              f'Number {n + 1}/{len(self.login_dict)}. \nLogging Out...')
                            self.problem_logins['email'].append(self.login_dict[n]['email'])
                            self.problem_logins['password'].append(self.login_dict[n]['password'])

                            df = pandas.DataFrame(self.problem_logins)
                            df.to_csv('static/problem_logs.csv')

                            log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                            log_out.click()

                        else:
                            date_of_meeting = driver.find_element(By.ID, 'CmisCellLeadersReport_date_of_meeting')
                            date_of_meeting.click()
                            date_of_meeting.send_keys(self.date)

                            new_attendance = choice(self.attendance)
                            new_first_timers = choice(self.first_timers)
                            new_new_converts = choice([new_first_timers - 3, new_first_timers - 4])
                            new_holy_spirit = choice([new_new_converts - 2, new_new_converts - 3])

                            new_midweek = choice(self.midweek)
                            new_church = choice(self.sunday)

                            testimony = driver.find_element(By.NAME, 'CmisCellLeadersReport[testimony]')
                            testimony.clear()
                            testimony.send_keys(choice(self.testimony_list))

                    elif i == 'bs1':
                        try:
                            type_of_meeting = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[1]'
                                                                            '/td[2]/div/div[2]/label/input')
                            type_of_meeting.click()
                        except ElementClickInterceptedException:
                            # -------------Close Pop Up----------------
                            not_necessary = driver.find_element(By.XPATH,
                                                                '//*[@id="onesignal-slidedown-cancel-button"]')
                            not_necessary.click()
                            # -------------Close Pop Up----------------
                            type_of_meeting = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[1]'
                                                                            '/td[2]/div/div[2]/label/input')
                            type_of_meeting.click()
                        except NoSuchElementException:
                            # global problem_status
                            problem_status = (f'Problem with {self.login_dict[n]["email"]}. '
                                              f'Number {n + 1}/{len(self.login_dict)}. \nLogging Out...')
                            self.problem_logins['email'].append(self.login_dict[n]['email'])
                            self.problem_logins['password'].append(self.login_dict[n]['password'])

                            df = pandas.DataFrame(self.problem_logins)
                            df.to_csv('static/problem_logs.csv')

                            log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                            log_out.click()

                        else:
                            date_of_meeting = driver.find_element(By.ID, 'CmisCellLeadersReport_date_of_meeting')
                            date_of_meeting.click()
                            date_of_meeting.send_keys(self.date)

                            new_attendance = choice(self.attendance)
                            new_first_timers = choice(self.first_timers)
                            new_new_converts = choice([new_first_timers - 3, new_first_timers - 4])
                            new_holy_spirit = choice([new_new_converts - 2, new_new_converts - 3])

                            new_midweek = choice(self.midweek)
                            new_church = choice(self.sunday)

                            testimony = driver.find_element(By.NAME, 'CmisCellLeadersReport[testimony]')
                            testimony.clear()
                            testimony.send_keys(choice(self.testimony_list))

                    elif i == 'bs2':
                        try:
                            type_of_meeting = driver.find_element(By.XPATH, 'c')
                            type_of_meeting.click()
                        except ElementClickInterceptedException:
                            # -------------Close Pop Up----------------
                            not_necessary = driver.find_element(By.XPATH,
                                                                '//*[@id="onesignal-slidedown-cancel-button"]')
                            not_necessary.click()
                            # -------------Close Pop Up----------------
                            type_of_meeting = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[1]'
                                                                            '/td[2]/div/div[3]/label/input')
                            type_of_meeting.click()
                        except NoSuchElementException:
                            # global problem_status
                            problem_status = (f'Problem with {self.login_dict[n]["email"]}. '
                                              f'Number {n + 1}/{len(self.login_dict)}. \nLogging Out...')
                            self.problem_logins['email'].append(self.login_dict[n]['email'])
                            self.problem_logins['password'].append(self.login_dict[n]['password'])

                            df = pandas.DataFrame(self.problem_logins)
                            df.to_csv('static/problem_logs.csv')

                            log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                            log_out.click()

                        else:
                            date_of_meeting = driver.find_element(By.ID, 'CmisCellLeadersReport_date_of_meeting')
                            date_of_meeting.click()
                            date_of_meeting.send_keys(self.date2)

                            new_attendance = choice(self.attendance)
                            new_first_timers = choice(self.first_timers)
                            new_new_converts = choice([new_first_timers - 3, new_first_timers - 4])
                            new_holy_spirit = choice([new_new_converts - 2, new_new_converts - 3])

                            new_midweek = choice(self.midweek)
                            new_church = choice(self.sunday)

                            testimony = driver.find_element(By.NAME, 'CmisCellLeadersReport[testimony]')
                            testimony.clear()
                            testimony.send_keys(choice(self.testimony_list))

                    elif i == 'cellcrusade':
                        try:
                            type_of_meeting = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[1]'
                                                                            '/td[2]/div/div[4]/label/input')
                            type_of_meeting.click()
                        except ElementClickInterceptedException:
                            # -------------Close Pop Up----------------
                            not_necessary = driver.find_element(By.XPATH,
                                                                '//*[@id="onesignal-slidedown-cancel-button"]')
                            not_necessary.click()
                            # -------------Close Pop Up----------------
                            type_of_meeting = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[1]'
                                                                            '/td[2]/div/div[4]/label/input')
                            type_of_meeting.click()
                        except NoSuchElementException:
                            # global problem_status
                            problem_status = (f'Problem with {self.login_dict[n]["email"]}. '
                                              f'Number {n + 1}/{len(self.login_dict)}. \nLogging Out...')
                            self.problem_logins['email'].append(self.login_dict[n]['email'])
                            self.problem_logins['password'].append(self.login_dict[n]['password'])

                            df = pandas.DataFrame(self.problem_logins)
                            df.to_csv('static/problem_logs.csv')

                            log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                            log_out.click()
                        else:
                            date_of_meeting = driver.find_element(By.ID, 'CmisCellLeadersReport_date_of_meeting')
                            date_of_meeting.click()
                            date_of_meeting.send_keys(self.date)

                            new_attendance = choice(self.attendance)
                            new_first_timers = choice(self.first_timers)
                            new_new_converts = choice([new_first_timers - 3, new_first_timers - 4])
                            new_holy_spirit = choice([new_new_converts - 2, new_new_converts - 3])

                            new_midweek = choice(self.midweek)
                            new_church = choice(self.sunday)

                            testimony = driver.find_element(By.NAME, 'CmisCellLeadersReport[testimony]')
                            testimony.clear()
                            testimony.send_keys(choice(self.testimony_list))

                    try:
                        attendance = driver.find_element(By.XPATH,
                                                         '//*[@id="CmisCellLeadersReport_total_no_at_cell_meeting"]')
                        attendance.clear()
                        attendance.send_keys(new_attendance)
                    # except NoSuchElementException:
                    #     # global problem_status
                    #     problem_status = (f'Problem with {self.login_dict[n]["email"]}. '
                    #                       f'Number {n + 1}/{len(self.login_dict)}. \nLogging Out...')
                    #     self.problem_logins['email'].append(self.login_dict[n]['email'])
                    #     self.problem_logins['password'].append(self.login_dict[n]['password'])
                    #
                    #     df = pandas.DataFrame(self.problem_logins)
                    #     df.to_csv('static/problem_logs.csv')
                    #
                    #     log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                    #     log_out.click()
                    except ElementNotInteractableException:
                        attendance = driver.find_element(By.XPATH,
                                                         '//*[@id="CmisCellLeadersReport_1_total_no_at_bible_study"]')
                        attendance.clear()
                        attendance.send_keys(new_attendance)

                    first_timers = driver.find_element(By.NAME, 'CmisCellLeadersReport[no_of_first_timers]')
                    first_timers.clear()
                    first_timers.send_keys(new_first_timers)

                    new_converts = driver.find_element(By.NAME, 'CmisCellLeadersReport[no_of_new_converts]')
                    new_converts.clear()
                    new_converts.send_keys(new_new_converts)

                    holy_spirit = driver.find_element(By.NAME, 'CmisCellLeadersReport[no_of_infilling]')
                    holy_spirit.clear()
                    holy_spirit.send_keys(new_holy_spirit)

                    midweek = driver.find_element(By.NAME,
                                                  'CmisCellLeadersReport[no_of_members_at_wed_service]')
                    midweek.clear()
                    midweek.send_keys(new_midweek)

                    sunday_service = driver.find_element(By.NAME,
                                                         'CmisCellLeadersReport[no_of_members_at_sun_service]')
                    sunday_service.clear()
                    sunday_service.send_keys(new_church)

                    # -------------------------------Time of meeting----------------------------------------------
                    try:
                        start_time = driver.find_element(By.XPATH, '//*[@id="_easyui_textbox_input1"]')
                        start_time.click()

                        start_hour = driver.find_element(By.XPATH,
                                                         '/html/body/div[2]/div/div[1]/div[2]/div/div[8]')
                        start_hour.click()

                        start_pm = driver.find_element(By.XPATH,
                                                       '/html/body/div[2]/div/div[1]/div[1]/div[4]/div[2]')
                        start_pm.click()

                        start_ok = driver.find_element(By.XPATH,
                                                       '/html/body/div[2]/div/div[2]/table/tbody/tr/td[1]/a')
                        start_ok.click()

                        end_time = driver.find_element(By.XPATH, '//*[@id="_easyui_textbox_input2"]')
                        end_time.click()

                        end_hour = driver.find_element(By.XPATH,
                                                       '/html/body/div[3]/div/div[1]/div[2]/div/div[9]')
                        end_hour.click()

                        end_pm = driver.find_element(By.XPATH,
                                                     '/html/body/div[3]/div/div[1]/div[1]/div[4]/div[2]')
                        end_pm.click()

                        end_ok = driver.find_element(By.XPATH,
                                                     '/html/body/div[3]/div/div[2]/table/tbody/tr/td[1]/a')
                        end_ok.click()
                    except ElementClickInterceptedException:
                        # -------------Close Pop Up----------------
                        not_necessary = driver.find_element(By.XPATH,
                                                            '//*[@id="onesignal-slidedown-cancel-button"]')
                        not_necessary.click()
                        # -------------Close Pop Up----------------
                        start_time = driver.find_element(By.XPATH, '//*[@id="_easyui_textbox_input1"]')
                        start_time.click()

                        start_hour = driver.find_element(By.XPATH,
                                                         '/html/body/div[2]/div/div[1]/div[2]/div/div[8]')
                        start_hour.click()

                        start_pm = driver.find_element(By.XPATH,
                                                       '/html/body/div[2]/div/div[1]/div[1]/div[4]/div[2]')
                        start_pm.click()

                        start_ok = driver.find_element(By.XPATH,
                                                       '/html/body/div[2]/div/div[2]/table/tbody/tr/td[1]/a')
                        start_ok.click()

                        end_time = driver.find_element(By.XPATH, '//*[@id="_easyui_textbox_input2"]')
                        end_time.click()

                        end_hour = driver.find_element(By.XPATH,
                                                       '/html/body/div[3]/div/div[1]/div[2]/div/div[9]')
                        end_hour.click()

                        end_pm = driver.find_element(By.XPATH,
                                                     '/html/body/div[3]/div/div[1]/div[1]/div[4]/div[2]')
                        end_pm.click()

                        end_ok = driver.find_element(By.XPATH,
                                                     '/html/body/div[3]/div/div[2]/table/tbody/tr/td[1]/a')
                        end_ok.click()
                    # ------------------------------End time of meeting section------------------------------------

                    submit = driver.find_element(By.XPATH, '//*[@id="fixed-table2"]/tbody/tr[13]/td[2]/input')
                    submit.click()
                global completed
                completed = f'{self.login_dict[n]["email"]}.'

                global logs_completed
                logs_completed = f'{n + 1} / {(len(self.login_dict))}'

                global logs_left
                logs_left = f'{(len(self.login_dict)) - (n + 1)}'

                # Log out
                try:
                    log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                    log_out.click()
                except ElementClickInterceptedException:
                    # -------------Close Pop Up----------------
                    not_necessary = driver.find_element(By.XPATH,
                                                        '//*[@id="onesignal-slidedown-cancel-button"]')
                    not_necessary.click()

                    log_out = driver.find_element(By.LINK_TEXT, 'Log out')
                    log_out.click()
                except NoSuchElementException:
                    pass

        global final_status
        final_status = (f'Completed. Submitted reports for {len(self.login_dict) - len(self.problem_logins["email"])} '
                        f'accounts')

        df = pandas.DataFrame(self.problem_logins)
        # print(df)
        df.to_csv('static/problem_logs.csv')
        driver.quit()
