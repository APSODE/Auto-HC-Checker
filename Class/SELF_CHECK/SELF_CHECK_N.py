from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
import datetime, json, os, random, time, discord


class READ_WRITE:
    def READ_JSON(FILE_DIR):
        """FILE_DIR에는 데이터를 읽어올 JSON데이터 파일 디렉토리를 입력해주세요.

        리턴
        --------
        READ_JSON(FILE_DIR = :func:`JSON_DIR`)\n
        ==> READ_USER_DATA[:func:`"KEY"`]
        """

        with open(f"{FILE_DIR}", "r", encoding="utf-8") as READ_USER_PROFILE:
            READ_USER_DATA = json.load(READ_USER_PROFILE)
            READ_USER_PROFILE.close()

        return READ_USER_DATA  # READ_USER_DATA타입 = DICT


class INTERNAL_FUNC:
    def __init__(self, DRIVER, TIME_OUT = 2):
        self.DRIVER = DRIVER
        self.TIME_OUT = TIME_OUT

    def DriverGet_CSS(self, CSS_SELECTOR):
        return self.DRIVER.find_element_by_css_selector(css_selector = CSS_SELECTOR)

    def DriverGet_XPATH(self, XPATH):
        return self.DRIVER.find_element_by_xpath(xpath = XPATH)

    def DriverGet_CLSNAME(self, CLSNAME):
        return self.DRIVER.find_element_by_class_name(name = CLSNAME)

    def DriverGet_Wait(self, ELEMENT):
        return WebDriverWait(driver = self.DRIVER, timeout = self.TIME_OUT).until(EC.presence_of_element_located(ELEMENT))


class SELF_CHECK_N:
    def __init__(self, DEBUG = False, TEST_TYPE = 0, RECURSIVE_LIMIT = 3, TIME_OUT = 3):
        self.DEBUG = DEBUG
        self.MSG = None
        self.RECURSIVE_COUNT = 0
        self.RECURSIVE_LIMIT = RECURSIVE_LIMIT
        self.TIME_OUT = TIME_OUT

        self.CH_DRIVER_DIR = ".\\chromedriver_win32\\chromedriver.exe" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\chromedriver_win32\\chromedriver.exe"
        self.XPATH_DATA_FILE_DIR = ".\\SELF_CHECK_CONFIG\\Self_Check_Xpath.json" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\SELF_CHECK_CONFIG\\Self_Check_Xpath.json"
        self.XPATH_DATA = READ_WRITE.READ_JSON(self.XPATH_DATA_FILE_DIR)
        self.USER_DATA_DIR_LIST = [(".\\AUTO_CHECK_USER_DATA\\" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\AUTO_CHECK_USER_DATA\\") + str(FILE_NAME) for FILE_NAME in os.listdir(".\\AUTO_CHECK_USER_DATA\\" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\AUTO_CHECK_USER_DATA\\")] if (DEBUG is False) else [(".\\AUTO_CHECK_USER_DATA\\이건보.json" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\AUTO_CHECK_USER_DATA\\이건보.json")] if TEST_TYPE == 0 else [(".\\AUTO_CHECK_USER_DATA\\" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\AUTO_CHECK_USER_DATA\\") + str(FILE_NAME) for FILE_NAME in os.listdir(".\\AUTO_CHECK_USER_DATA\\" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\AUTO_CHECK_USER_DATA\\")]

        self.CONFIG_DIR = ".\\SELF_CHECK_CONFIG\\Self_Check_Config.json" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\SELF_CHECK_CONFIG\\Self_Check_Config.json"
        self.CONFIG_DATA = READ_WRITE.READ_JSON(self.CONFIG_DIR)
        self.RT_USER_LIST = {
            "S": [],
            "F": [],
            "E": [],
            "P": []
        }

    @staticmethod
    def ReturnBtnCSS(USER_PASSWORD=None):
        if USER_PASSWORD is None:
            raise ValueError("USER_PASSWORD는 무조건 입력되어야 합니다.")
        return [f'a[aria-label="{USER_PASS_PART}"]' for USER_PASS_PART in USER_PASSWORD]

    @staticmethod
    def ReturnSurveyCSS(SCHOOL, WEEKDAY):
        """
        운양고 : 수요일 / 금요일 ==> 자가진단 설문항목 음성 판정으로 설문
        제일고 : 월요일 / 수요일 ==> 자가진단 설문항목 음성 판정으로 설문
        사우고 : 수요일 / 토요일 ==> 자가진단 설문항목 음성 판정으로 설문
        :param SCHOOL:
        :param WEEKDAY:
        :return SURVEY_CSS_SELECTOR_LIST:
        """
        QUALIFICATION = None
        if "제일" in SCHOOL or "사우" in SCHOOL: #자가진단 음성 설문 필요 날짜 ==> 월 목
            QUALIFICATION = WEEKDAY == 0 or WEEKDAY == 3

        if "운양" in SCHOOL: #자가진단 음성 설문 필요 날짜 ==> 수 금
            QUALIFICATION = WEEKDAY == 2 or WEEKDAY == 4


        return [f'label[for="survey_q{QUESTION_NUM + 1}a{1 if QUALIFICATION and (True if QUESTION_NUM + 1 == 2 else False) else (3 if QUESTION_NUM + 1 == 2 else 1) }"]' for QUESTION_NUM in range(3)]

    @staticmethod
    def RefreshUserData(USER_NAME, USER_PASS, USER_BIRTH, USER_SCHOOL):
        USER_DATA_FILE_DIR = ".\\AUTO_CHECK_USER_DATA\\" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\AUTO_CHECK_USER_DATA\\" + str(USER_NAME) + ".json"
        DIR_CHECK = os.path.exists(USER_DATA_FILE_DIR)
        if DIR_CHECK:
            USER_DATA = {
                "USER_NAME": USER_NAME,
                "USER_BIRTH": USER_BIRTH,
                "USER_PASS": USER_PASS,
                "USER_SCHOOL": USER_SCHOOL
            }
            with open(USER_DATA_FILE_DIR, "w", encoding = "utf-8") as WRITE_FILE:
                json.dump(USER_DATA, WRITE_FILE, indent = 4)
            return [True, USER_DATA]
        else:
            return [False, "기존 데이터파일이 존재하지 않습니다. 등록을 먼저 진행하여 주십시오"]

    @staticmethod
    def WriteErrorLog(ERROR_MSG, XPATH_NUM):
        with open(f".\\ERROR_LOG\\ERROR_LOG {str(datetime.datetime.today()).split(' ')[0]}.txt", "a") as WRITE_FILE:
            WRITE_FILE.write(f"ERROR : OCCURRENCE TIME = {str(datetime.datetime.today()).split('.')[0]},\nXPATH_NUM = {XPATH_NUM},\nMESSAGE = {ERROR_MSG}")

    def ShowTimePreset(self):
        READ_CONFIG_DATA = self.CONFIG_DATA
        RT_EMBED = discord.Embed(title = ":alarm_clock:자가진단 타임 프리셋:alarm_clock:", description = "")
        for TIME_PRESET_NUM in READ_CONFIG_DATA["TIME_LIST"]:
            TIME_PRESET = READ_CONFIG_DATA["TIME_LIST"][TIME_PRESET_NUM]
            RT_EMBED.add_field(name = f"{TIME_PRESET_NUM}", value = f"{TIME_PRESET['BASETIME_HOUR']}시 {TIME_PRESET['BASETIME_MIN']}분 {TIME_PRESET['BASETIME_SEC']}초\n활성화 여부 : `{True if TIME_PRESET['TODAY_BASETIME'] == 1 else False}`")
        return RT_EMBED

    def SetTimePreset(self, SET_TIME_PRESET_NUM):
        with open(self.CONFIG_DIR, "w", encoding = "utf-8") as WRITE_FILE:
            READ_CONFIG_DATA = self.CONFIG_DATA
            for TIME_PRESET_NUM in READ_CONFIG_DATA["TIME_LIST"]:
                TIME_PRESET_ACTIVE_CHECK = READ_CONFIG_DATA["TIME_LIST"][TIME_PRESET_NUM]["TODAY_BASETIME"] == 1
                if TIME_PRESET_ACTIVE_CHECK is True:
                    READ_CONFIG_DATA["TIME_LIST"][TIME_PRESET_NUM]["TODAY_BASETIME"] = 0
                else:
                    pass
            READ_CONFIG_DATA["TIME_LIST"][SET_TIME_PRESET_NUM]["TODAY_BASETIME"] = 1
            json.dump(READ_CONFIG_DATA, WRITE_FILE, indent = 4)
        return discord.Embed(title = ":alarm_clock:자가진단 타임 프리셋 변경:alarm_clock:", description = f"자가진단 타임프리셋이 `{SET_TIME_PRESET_NUM}번`타임프리셋으로 변경되었습니다. ")

    def TimeCheck(self):
        TD = datetime.datetime.today()
        TD_W = TD.weekday()
        TD_D = str(TD).split(" ")[0]
        TD_H = TD.hour
        TD_M = TD.minute
        TD_S = TD.second



        BF_CHECK_TIME_DATA = self.CONFIG_DATA["WHETHER_TODAY_SELF_CHECK"]["TODAY_SELF_CHECK_DATE"]
        BF_CHECK_TF = self.CONFIG_DATA["WHETHER_TODAY_SELF_CHECK"]["TODAY_SELF_CHECK"]

        if BF_CHECK_TIME_DATA != TD_D:
            with open(self.CONFIG_DIR, "w", encoding = "utf-8") as WRITE_CONFIG_FILE:
                self.CONFIG_DATA["WHETHER_TODAY_SELF_CHECK"]["TODAY_SELF_CHECK_DATE"] = TD_D
                if BF_CHECK_TF == 1:
                    self.CONFIG_DATA["WHETHER_TODAY_SELF_CHECK"]["TODAY_SELF_CHECK"] = 0
                json.dump(self.CONFIG_DATA, WRITE_CONFIG_FILE, indent = 4)
            self.CONFIG_DATA = READ_WRITE.READ_JSON(self.CONFIG_DIR)
        else:
            pass

        CONFIG_TIME_TABLE = self.CONFIG_DATA["TIME_LIST"]


        TIME_TABLE_LIST = [TABLE for TABLE in CONFIG_TIME_TABLE]
        SELECTED_TIME_TABLE = None
        for TABLE_NUM in TIME_TABLE_LIST:
            TIME_TABLE = CONFIG_TIME_TABLE[TABLE_NUM]
            if TIME_TABLE["TODAY_BASETIME"] == 1:
                SELECTED_TIME_TABLE = [TIME_TABLE, TABLE_NUM]
                break
            else:
                pass



        BF_CHECK_QUALIFICATION = BF_CHECK_TF == 0 if self.DEBUG is False else True


        if BF_CHECK_QUALIFICATION:
            TIME_TABLE_H = SELECTED_TIME_TABLE[0]["BASETIME_HOUR"]
            TIME_TABLE_M = SELECTED_TIME_TABLE[0]["BASETIME_MIN"]
            TIME_TABLE_S = SELECTED_TIME_TABLE[0]["BASETIME_SEC"]

            WEEKEND_CHECK = TD_W < 5
            TIME_CHECK_H = TIME_TABLE_H == TD_H
            TIME_CHECK_M = TIME_TABLE_M == TD_M
            TIME_CHECK_S = TIME_TABLE_S == TD_S

            TIME_CHECK_QUALIFICATION = (TIME_CHECK_H and TIME_CHECK_M and TIME_CHECK_S and WEEKEND_CHECK) if self.DEBUG is False else True

            if TIME_CHECK_QUALIFICATION:

                self.CONFIG_DATA["TIME_LIST"][SELECTED_TIME_TABLE[1]]["TODAY_BASETIME"] = 0


                with open(self.CONFIG_DIR, "w", encoding = "utf-8") as WRITE_CONFIG_FILE:
                    RND_TABLE = None
                    for _ in range(10):
                        RND_TABEL = str(random.randint(1, self.CONFIG_DATA["TIME_LIST"].__len__()))
                    self.CONFIG_DATA["TIME_LIST"][RND_TABEL]["TODAY_BASETIME"] = 1
                    self.CONFIG_DATA["WHETHER_TODAY_SELF_CHECK"]["TODAY_SELF_CHECK_DATE"] = TD_D
                    self.CONFIG_DATA["WHETHER_TODAY_SELF_CHECK"]["TODAY_SELF_CHECK"] = 1
                    json.dump(self.CONFIG_DATA, WRITE_CONFIG_FILE, indent = 4)

                return True

            else:
                return False

        else:
            return False

    def StartCheck(self):
        SHUFFLE_COUNT = random.randint(5, 10)
        USER_DATA_FILE_DIR_LIST = self.USER_DATA_DIR_LIST if self.RT_USER_LIST["F"].__len__() == 0 else [(".\\AUTO_CHECK_USER_DATA\\" if __name__ == "__main__" else ".\\Class\\SELF_CHECK\\AUTO_CHECK_USER_DATA\\") + str(F_USER_DIR) + ".json" for F_USER_DIR in self.RT_USER_LIST["F"]]
        print(f"USER_COUNT = {USER_DATA_FILE_DIR_LIST.__len__()}명\nSUCCESS_USER = {self.RT_USER_LIST['S']}\nFAIL_USER = {self.RT_USER_LIST['F']}\nERROR_USER = {self.RT_USER_LIST['E']}")
        self.RT_USER_LIST["F"] = []

        for _ in range(SHUFFLE_COUNT):
            random.shuffle(USER_DATA_FILE_DIR_LIST)

        for USER_DATA_FILE in USER_DATA_FILE_DIR_LIST:
            READ_USER_DATA = READ_WRITE.READ_JSON(USER_DATA_FILE)
            self.DriverLoad(USER_DATA = READ_USER_DATA)

        if self.RT_USER_LIST["F"].__len__() != 0 and self.RECURSIVE_COUNT < self.RECURSIVE_LIMIT:
            self.RECURSIVE_COUNT += 1
            print("재귀 호출 성공")
            self.StartCheck()

        return self.RT_USER_LIST

    def DriverLoad(self, USER_DATA = None):
        if USER_DATA is None:
            raise ValueError("USER_DATA를 전달받지 못하였습니다.")

        USER_NAME = USER_DATA["USER_NAME"]
        USER_BIRTH = USER_DATA["USER_BIRTH"]
        USER_PASS = USER_DATA["USER_PASS"]
        USER_SCHOOL = USER_DATA["USER_SCHOOL"]

        SELF_CHECK_URL_FIRST = "https://hcs.eduro.go.kr/#/loginHome"
        SELF_CHECK_URL_SECOND = "https://hcs.eduro.go.kr/#/loginWithUserInfo"
        SECURE_CSS_SELECTOR = "body > app-root:nth-child(3) > div > div:nth-child(1) > div#container:nth-child(3) > div.subpage > div.contents:nth-child(2) > div > div#WriteInfoForm:nth-child(2) > table > tbody:nth-child(3) > tr > td:nth-child(2) > div.flexUnit > button.keyboard-icon:nth-child(2) > img.keyboard-img"

        OPTION = webdriver.ChromeOptions()
        for OP in ["headless", "disable-gpu"]:
            OPTION.add_argument(OP)
        # WEBDRIVER = webdriver.Chrome(self.CH_DRIVER_DIR, options = OPTION) if self.DEBUG is False else webdriver.Chrome(self.CH_DRIVER_DIR)
        WEBDRIVER = webdriver.Chrome(self.CH_DRIVER_DIR, options = OPTION)



        IN_FUNC = INTERNAL_FUNC(DRIVER=WEBDRIVER, TIME_OUT = self.TIME_OUT)
        WEBDRIVER.implicitly_wait(time_to_wait = self.TIME_OUT)
        WEBDRIVER.get(SELF_CHECK_URL_FIRST)
        WEBDRIVER.get(SELF_CHECK_URL_SECOND)
        CURRENT_URL_CHECK = WEBDRIVER.current_url == SELF_CHECK_URL_SECOND
        if CURRENT_URL_CHECK is False:
            WEBDRIVER.get(SELF_CHECK_URL_SECOND)
        else:
            pass

        ERROR_COUNT = 0
        for XPATH_NUM in self.XPATH_DATA["XPATH"]:
            CURRENT_XPATH = self.XPATH_DATA["XPATH"][XPATH_NUM]
            if XPATH_NUM == "4":
                try:
                    IN_FUNC.DriverGet_Wait(ELEMENT = (By.XPATH, CURRENT_XPATH)).send_keys(USER_SCHOOL)
                except Exception as MSG:
                    ERROR_COUNT += 1
                    self.WriteErrorLog(ERROR_MSG=MSG, XPATH_NUM=XPATH_NUM)
                    break

            elif XPATH_NUM == "8":
                try:
                    IN_FUNC.DriverGet_Wait(ELEMENT=(By.XPATH, CURRENT_XPATH)).send_keys(USER_NAME)
                except Exception as MSG:
                    ERROR_COUNT += 1
                    self.WriteErrorLog(ERROR_MSG=MSG, XPATH_NUM=XPATH_NUM)
                    break

            elif XPATH_NUM == "9":
                try:
                    IN_FUNC.DriverGet_Wait(ELEMENT=(By.XPATH, CURRENT_XPATH)).send_keys(USER_BIRTH)
                except Exception as MSG:
                    ERROR_COUNT += 1
                    self.WriteErrorLog(ERROR_MSG=MSG, XPATH_NUM=XPATH_NUM)
                    break

            elif XPATH_NUM == "11":
                try:
                    ELEM = IN_FUNC.DriverGet_Wait(ELEMENT = (By.CSS_SELECTOR, 'strong[data-v-08a9b588]'))
                    print(f"!!ERROR OCCURRED!!\nUSER = {USER_NAME}, XPATH_NUM = {XPATH_NUM}, ERROR_REASON = 개인정보 수집 및 이용 동의서 미동의 유저")
                    ERROR_COUNT += 2
                    break
                except TimeoutException:
                    try:
                        IN_FUNC.DriverGet_Wait(ELEMENT = (By.CSS_SELECTOR, SECURE_CSS_SELECTOR)).click()
                        for USER_PASS_CSS_SELECTOR in self.ReturnBtnCSS(USER_PASSWORD = USER_PASS):
                            IN_FUNC.DriverGet_Wait(ELEMENT = (By.CSS_SELECTOR, USER_PASS_CSS_SELECTOR)).click()
                    except TimeoutException:
                        try:
                            IN_FUNC.DriverGet_Wait(ELEMENT=(By.CSS_SELECTOR, 'input[value="확인 / Confirm"]')).click()
                            IN_FUNC.DriverGet_Wait(ELEMENT=(By.CSS_SELECTOR, SECURE_CSS_SELECTOR)).click()
                            for USER_PASS_CSS_SELECTOR in self.ReturnBtnCSS(USER_PASSWORD=USER_PASS):
                                IN_FUNC.DriverGet_Wait(ELEMENT=(By.CSS_SELECTOR, USER_PASS_CSS_SELECTOR)).click()
                        except Exception as MSG:
                            ERROR_COUNT += 1
                            self.WriteErrorLog(XPATH_NUM = XPATH_NUM, ERROR_MSG = MSG)
                            break

            elif XPATH_NUM == "13":
                try:
                    ELEM = IN_FUNC.DriverGet_Wait(ELEMENT = (By.CSS_SELECTOR, 'a[class="survey-button active"]'))
                    print(f"유저 '{USER_NAME}'님은 이미 자가진단을 진행하였습니다.")
                    if self.DEBUG is False:
                        break
                    else:
                        try:
                            ELEM.click()
                        except Exception as MSG:
                            ERROR_COUNT += 1
                            self.WriteErrorLog(ERROR_MSG=MSG, XPATH_NUM=XPATH_NUM)
                            break

                except UnexpectedAlertPresentException:
                    ERROR_COUNT += 3
                    print(f"!!ERROR OCCURRED!!\nUSER = {USER_NAME}, XPATH_NUM = {XPATH_NUM}, ERROR_REASON = 비밀번호 오류")
                    break

                except TimeoutException:
                    try:
                        IN_FUNC.DriverGet_Wait(ELEMENT = (By.CSS_SELECTOR, 'a[class="survey-button"]')).click()
                    except Exception as MSG:
                        ERROR_COUNT += 1
                        self.WriteErrorLog(ERROR_MSG = MSG, XPATH_NUM = XPATH_NUM)
                        break

            elif XPATH_NUM == "14":
                try:
                    SURVEY_CSS_SELECTOR_LIST = self.ReturnSurveyCSS(SCHOOL = USER_SCHOOL, WEEKDAY = datetime.datetime.today().weekday())
                    for SURVEY_CSS_SELECTOR in SURVEY_CSS_SELECTOR_LIST:
                        IN_FUNC.DriverGet_Wait(ELEMENT = (By.CSS_SELECTOR, SURVEY_CSS_SELECTOR)).click()

                except Exception as MSG:
                    ERROR_COUNT += 1
                    self.WriteErrorLog(XPATH_NUM = XPATH_NUM, ERROR_MSG = MSG)
                    break
            elif XPATH_NUM == "15":
                if self.DEBUG is True:
                    break
                elif self.DEBUG is False:
                    try:
                        IN_FUNC.DriverGet_Wait(ELEMENT = (By.CSS_SELECTOR, 'input[type="submit"][id="btnConfirm"][value="제출 / Submit"]')).click()
                    except Exception as MSG:
                        ERROR_COUNT += 1
                        self.WriteErrorLog(XPATH_NUM = XPATH_NUM, ERROR_MSG = MSG)
                        break
            else:
                try:
                    IN_FUNC.DriverGet_Wait(ELEMENT=(By.XPATH, CURRENT_XPATH)).click()
                except Exception as MSG:
                    ERROR_COUNT += 1
                    self.WriteErrorLog(XPATH_NUM=XPATH_NUM, ERROR_MSG=MSG)
                    break
        # time.sleep(0.5)
        WEBDRIVER.quit()
        if ERROR_COUNT == 0 and USER_NAME not in [ERROR_USER_DATA["USER_NAME"] for ERROR_USER_DATA in self.RT_USER_LIST["E"]]:
            self.RT_USER_LIST["S"].append(USER_NAME)
        elif ERROR_COUNT == 1:
            self.RT_USER_LIST["F"].append(USER_NAME)
        elif ERROR_COUNT == 2:
            self.RT_USER_LIST["E"].append({"USER_NAME": USER_NAME,"ERROR_REASON": "자가진단에 사용되는 개인정보에 대한 수집 동의를 하지 않으셨습니다.\n자가진단 사이트나 공식앱으로 접속하여 먼저 동의서에 동의를 해주십시오."})
        elif ERROR_COUNT == 3:
            self.RT_USER_LIST["P"].append({"USER_NAME": USER_NAME,"ERROR_REASON": "현재 유저데이터에 등록된 비밀번호가 잘못되어있습니다. \n **`$자가진단정보재등록`**명령어를 통해 재등록을 해주십시오. (사용법 : **`$등록방법`**)"})

    def JsonRW_Tool(self):
        XPATH_DATA = self.XPATH_DATA
        with open(self.XPATH_DATA_FILE_DIR, "w", encoding = "utf-8") as WRITE_FILE:
            for NUM in range(20):
                XPATH_DATA["XPATH_N"][f"{NUM + 1}"] = ""
            json.dump(self.XPATH_DATA, WRITE_FILE, indent = 4)


if __name__ == "__main__":
    SELF_CHECKER = SELF_CHECK_N(DEBUG = True, TEST_TYPE = 0, RECURSIVE_LIMIT = 2, TIME_OUT = 1)
    # SELF_CHECKER = SELF_CHECK_N()
    F_TIME = time.perf_counter()
    RT = SELF_CHECKER.StartCheck()
    S_TIME = time.perf_counter()
    print(f"결과 : {RT}\n소요시간 : {round((S_TIME - F_TIME), 2)}초")

    #제작 완료
