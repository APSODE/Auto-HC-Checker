from discord.ext import commands, tasks
from Class.SELF_CHECK.SELF_CHECK_N import READ_WRITE, SELF_CHECK_N
import discord, time, json


class INTERNAL_FUNC:
    @staticmethod
    def ReturnChannel(BOT):
        return [BOT.get_channel(CHANNEL_ID) for CHANNEL_ID in READ_WRITE.READ_JSON("MAIN_CONFIG.json")["CHANNEL_ID_LIST"]]


bot = commands.Bot(command_prefix ="&")


@bot.event
async def on_ready():
    print("\n=============\n 실 행 완 료 \n=============\n")
    await bot.change_presence(status = discord.Status.online, activity = discord.Game("자가진단"))
    Auto_HC_SelfCheck.start()


@tasks.loop(seconds = 1)
async def Auto_HC_SelfCheck():
    AUTO_HC_SELF_CHECKER = SELF_CHECK_N(RECURSIVE_LIMIT=3, TIME_OUT=3)
    TIME_CHECK = AUTO_HC_SELF_CHECKER.TimeCheck()
    # print(TIME_CHECK)
    if TIME_CHECK:
        F_TIME = time.perf_counter()
        RT_USER_LIST = AUTO_HC_SELF_CHECKER.StartCheck()
        S_TIME = time.perf_counter()
        RUNNING_TIME = f"총 소요시간 : {round((S_TIME - F_TIME), 2)}초"
        RT_EMBED_LIST = []

        if RT_USER_LIST["S"].__len__() > 0:
            RT_EMBED = discord.Embed(title=":white_check_mark:자가진단 완료자 명단:white_check_mark:", description="")
            for USER_NAME_NUM in range(RT_USER_LIST["S"].__len__()):
                USER_NAME = RT_USER_LIST["S"][USER_NAME_NUM]
                RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
            RT_EMBED.set_footer(text=RUNNING_TIME)
            RT_EMBED_LIST.append(RT_EMBED)

        if RT_USER_LIST["F"].__len__() > 0:
            RT_EMBED = discord.Embed(title=":warning:자가진단 실패자 명단:warning:", description="")
            for USER_NAME_NUM in range(RT_USER_LIST["F"].__len__()):
                USER_NAME = RT_USER_LIST["F"][USER_NAME_NUM]
                RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
            RT_EMBED.set_footer(text=RUNNING_TIME)
            RT_EMBED_LIST.append(RT_EMBED)

        if RT_USER_LIST["E"].__len__() > 0:
            RT_EMBED = discord.Embed(title=":warning:자가진단 오류 발생자 명단:warning:", description="")
            ERROR_REASON = None
            for USER_NAME_NUM in range(RT_USER_LIST["E"].__len__()):
                USER_NAME = RT_USER_LIST["E"][USER_NAME_NUM]["USER_NAME"]
                ERROR_REASON = RT_USER_LIST["E"][USER_NAME_NUM]["ERROR_REASON"]
                RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
            RT_EMBED.add_field(name=f"사유", value=f"{ERROR_REASON}", inline=False)
            RT_EMBED.set_footer(text=RUNNING_TIME)
            RT_EMBED_LIST.append(RT_EMBED)

        if RT_USER_LIST["P"].__len__() > 0:
            RT_EMBED = discord.Embed(title=":warning:자가진단 비밀번호 오류 발생자 명단:warning:", description="")
            ERROR_REASON = None
            for USER_NAME_NUM in range(RT_USER_LIST["P"].__len__()):
                USER_NAME = RT_USER_LIST["P"][USER_NAME_NUM]["USER_NAME"]
                ERROR_REASON = RT_USER_LIST["P"][USER_NAME_NUM]["ERROR_REASON"]
                RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
            RT_EMBED.add_field(name=f"사유", value=f"{ERROR_REASON}", inline=False)
            RT_EMBED.set_footer(text=RUNNING_TIME)
            RT_EMBED_LIST.append(RT_EMBED)

        for CHANNEL in INTERNAL_FUNC.ReturnChannel(BOT = bot):
            for RT_EMBED in RT_EMBED_LIST:
                await CHANNEL.send(embed=RT_EMBED)
    else:
        pass


@bot.command(aliases = ["자가진단"])
async def SelfCheck(ctx, *arg):
    try:
        if arg.__len__() == 1:
            if arg[0] == "타임프리셋":
                AUTO_HC_SELF_CHECKER = SELF_CHECK_N()
                await ctx.send(embed=AUTO_HC_SELF_CHECKER.ShowTimePreset())
        elif arg.__len__() == 2:
            if arg[0] == "프리셋설정":
                AUTO_HC_SELF_CHECKER = SELF_CHECK_N()
                await ctx.send(embed=AUTO_HC_SELF_CHECKER.SetTimePreset(SET_TIME_PRESET_NUM=str(arg[1])))

            elif arg[0] == "수동시작":
                AUTO_HC_SELF_CHECKER = SELF_CHECK_N(DEBUG = False if str(arg)[1].upper() == "FALSE" else True, TEST_TYPE = 1, RECURSIVE_LIMIT = 4, TIME_OUT = 2)
                await ctx.send(f"## 테스트 파라미터 정보 ##\nDEBUG = {False if str(arg)[1].upper() == 'FALSE' else True}\nTEST_TYPE = 1\nRECURSIVE_LIMIT = 4\nTIME_OUT = 2")

                F_TIME = time.perf_counter()
                RT_USER_LIST = AUTO_HC_SELF_CHECKER.StartCheck()
                S_TIME = time.perf_counter()
                RUNNING_TIME = f"총 소요시간 : {round((S_TIME - F_TIME), 2)}초"
                DESCRIPTION_TEXT = "" if str(arg).upper() == "FALSE" else "기능테스트이므로 실제 자가진단은 완료되지 않습니다."

                RT_EMBED_LIST = []
                if RT_USER_LIST["S"].__len__() > 0:
                    RT_EMBED = discord.Embed(title=":white_check_mark:자가진단 완료자 명단:white_check_mark:",description=f"{DESCRIPTION_TEXT}")
                    for USER_NAME_NUM in range(RT_USER_LIST["S"].__len__()):
                        USER_NAME = RT_USER_LIST["S"][USER_NAME_NUM]
                        RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
                    RT_EMBED.set_footer(text=RUNNING_TIME)
                    RT_EMBED_LIST.append(RT_EMBED)

                if RT_USER_LIST["F"].__len__() > 0:
                    RT_EMBED = discord.Embed(title=":warning:자가진단 실패자 명단:warning:", description=f"{DESCRIPTION_TEXT}")
                    for USER_NAME_NUM in range(RT_USER_LIST["F"].__len__()):
                        USER_NAME = RT_USER_LIST["F"][USER_NAME_NUM]
                        RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
                    RT_EMBED.set_footer(text=RUNNING_TIME)
                    RT_EMBED_LIST.append(RT_EMBED)

                if RT_USER_LIST["E"].__len__() > 0:
                    RT_EMBED = discord.Embed(title=":warning:자가진단 오류 발생자 명단:warning:",
                                             description=f"{DESCRIPTION_TEXT}")
                    ERROR_REASON = None
                    for USER_NAME_NUM in range(RT_USER_LIST["E"].__len__()):
                        USER_NAME = RT_USER_LIST["E"][USER_NAME_NUM]["USER_NAME"]
                        ERROR_REASON = RT_USER_LIST["E"][USER_NAME_NUM]["ERROR_REASON"]
                        RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
                    RT_EMBED.add_field(name=f"사유", value=f"{ERROR_REASON}", inline=False)
                    RT_EMBED.set_footer(text=RUNNING_TIME)
                    RT_EMBED_LIST.append(RT_EMBED)

                if RT_USER_LIST["P"].__len__() > 0:
                    RT_EMBED = discord.Embed(title=":warning:자가진단 비밀번호 오류 발생자 명단:warning:",
                                             description=f"{DESCRIPTION_TEXT}")
                    ERROR_REASON = None
                    for USER_NAME_NUM in range(RT_USER_LIST["P"].__len__()):
                        USER_NAME = RT_USER_LIST["P"][USER_NAME_NUM]["USER_NAME"]
                        ERROR_REASON = RT_USER_LIST["P"][USER_NAME_NUM]["ERROR_REASON"]
                        RT_EMBED.add_field(name=f"{USER_NAME_NUM + 1}번", value=f"{USER_NAME}")
                    RT_EMBED.add_field(name=f"사유", value=f"{ERROR_REASON}", inline=False)
                    RT_EMBED.set_footer(text=RUNNING_TIME)
                    RT_EMBED_LIST.append(RT_EMBED)

                for CHANNEL in INTERNAL_FUNC.ReturnChannel(BOT = bot):
                    for RT_EMBED in RT_EMBED_LIST:
                        await CHANNEL.send(embed=RT_EMBED)
        else:
            await ctx.send("명령어를 다시 확인하여 주십시오.")

    except Exception as MSG:
        await ctx.send(f"!!ERROR OCCURRED!!\nERROR_MESSAGE = {MSG}")


@bot.command(aliases = ["공지"])
async def announcement(ctx, *arg):
    try:
        if arg.__len__() == 0:
            await ctx.send(embed = discord.Embed(title=":bangbang: 공지 :bangbang:", description=f"{READ_WRITE.READ_JSON('MAIN_CONFIG.json')['ANNOUNCEMENT']}"))
        elif arg.__len__() >= 2:
            if arg[0] == "수정":
                LIST = list(arg)
                del LIST[0]

                READ_CONFIG_DATA = READ_WRITE.READ_JSON("MAIN_CONFIG.json")
                try:
                    with open("MAIN_CONFIG.json", "w", encoding = "utf-8") as WRITE_FILE:
                        EDIT_TEXT = ""
                        for PART_TEXT in LIST:
                            EDIT_TEXT += PART_TEXT + " "
                        READ_CONFIG_DATA["ANNOUNCEMENT"] = EDIT_TEXT
                        json.dump(READ_CONFIG_DATA, WRITE_FILE, indent = 4)
                    await ctx.send("공지를 성공적으로 변경하였습니다.")
                except Exception as MSG:
                    await ctx.send(f"!!ERROR OCCURRED!!\nERROR_MESSAGE = {MSG}")
        else:
            await ctx.send("명령어를 다시 확인하여 주십시오.")
    except Exception as MSG:
        await ctx.send(f"!!ERROR OCCURRED!!\nERROR_MESSAGE = {MSG}")


bot.run(READ_WRITE.READ_JSON("MAIN_CONFIG.json")["TOKEN"])

