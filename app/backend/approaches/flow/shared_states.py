from azure.data.tables import UpdateMode
from typing import Callable

from approaches.requestcontext import RequestContext

StateStartIntro = "START_INTRO"
StateStartPreperation = "START_PREPERATION"
StateStartISP = "START_ISP"
StateStartPositiveCognition = "START_POSITIVE_COGNITION"

StateAskIfToExit = "ASK_IF_TO_EXIT"
StateExit = "EXIT"
StateEndInput = "END_INPUT"

States = {}

VariableClientId = "clientId"
VariableDistressLevel = "prefixByDistressLevel"
VariableExitText = "exitText"
VariableFirstDistressLevel = "firstDistressLevel"
VariableIsBotMale = "isBotMale"
VariableIsPatientMale = "isPatientMale"
VariableIspPath = "ispPath"
VariableIsUserExited = "isUserExited"
VariablePatientName = "patientName"
VariableShouldSaveClientStatus = "shouldSaveClientStatus"
VariableSumDistressLevel = "sumDistressLevel"
VariableVideoIndex = "videoIndex"
VariableWasDistressLevelIncreased = "wasDistressLevelIncreased"
VariableWasDistressLevelIncreasedTwice = "wasDistressLevelIncreasedTwice"

PartitionKey = "DefaultPartition"
DemoClientId = "דמו"
MissingClientId = "כניסה ללא זיהוי משתמש"
ContactsText = """טלפון מרכז החוסן הארצי הטיפולי *5486 (פתוח בימים א-ה בין 8.00-20.00)
טלפון ער"ן  טלפון 1201 או  <a href="https://api.whatsapp.com/send/?phone=%2B972545903462&text&type=phone_number&app_absent=0">ווטסאפ</a> (השירות מוגש לכל מצוקה ובמגוון שפות, וניתן בצורה אנונימית ומיידית, 24 שעות ביממה בכל ימות השנה)"""
GenericExitText = """תודה שהתעניינת בכלי לסיוע עצמי במצבי מצוקה. 
הרבה פעמים אחרי שחווים אירוע מאיים או קשה, או במצבים שחוששים מאירועים כאלה, חווים קושי או מצוקה. יש לך אפשרות לפנות לסיוע נפשי ולקבל כלים אחרים בגופים שונים כגון
{contactsText}""".format(contactsText = ContactsText)

ChatInputNotWait = "INTERNAL_PLACEHOLDER_NOT_WAIT"
ChatInputFreeText = { "inputType": "freeText" }
ChatInputNumeric = { "inputType": "numeric" }
ChatInputDisabled = { "inputType": "disabled" }
def chat_input_multiple_options(options: list[str]):
    return { "inputType": "multiple", "options": options }
def chat_input_slider(minValue, minLabel, maxValue, maxLabel):
    return { "inputType": "slider", "minValue": minValue, "minLabel": minLabel, "maxValue": maxValue, "maxLabel": maxLabel }

def get_exit_text(request_context: RequestContext):
    is_patient_male = request_context.get_var(VariableIsPatientMale)
    is_bot_male = request_context.get_var(VariableIsBotMale)
    is_user_exited = request_context.get_var(VariableIsUserExited)
    first_distress = request_context.get_var(VariableFirstDistressLevel)
    last_distress = request_context.get_var(VariableDistressLevel)
    sum_distress_level = request_context.get_var(VariableSumDistressLevel)
    was_distress_level_increased = request_context.get_var(VariableWasDistressLevelIncreased)
    was_distress_level_increased_twice = request_context.get_var(VariableWasDistressLevelIncreasedTwice)
    video_index = request_context.get_var(VariableVideoIndex)
    contacts = """
{contactsText}""".format(contactsText = ContactsText)
    if was_distress_level_increased_twice or (was_distress_level_increased and is_user_exited) or (first_distress <= last_distress):
        return """לפני שנסיים אני רוצה להזכיר לך שהתגובות שחווית מאוד הגיוניות. הרבה פעמים אחרי שחווים אירוע מאיים או קשה או במצבים שחוששים מאירועים כאלה חווים קושי או מצוקה. אני רוצה לציין בפניך את העובדה שיש לך אפשרות לפנות לסיוע נפשי ולקבל כלים אחרים בגופים שונים כגון:{contacts}""".format(
            contacts = contacts)

    if video_index == 7 and first_distress > last_distress:
        improvement_description = "שתיארת שיפור בין תחילת התרגול לסיומו ולעודד אותך לעשות שימוש בתרגול שעשינו"
    elif video_index == 7 and sum_distress_level / 8 < first_distress:
        improvement_description = "שבמהלך התרגול תיארת נקודות של שיפור ולכן תוכל לבחור לעשות שימוש בתרגול שעשינו".format(can_choose = "תוכל לבחור" if is_bot_male else "תוכלי לבחור")
    else:
        improvement_description = "שתיארת שיפור בעקבות התרגול ולעודד אותך לעשות שימוש בתרגול שעשינו"

    return """לפני שנסיים אני רוצה להזכיר לך שהתגובות שחווית מאוד הגיוניות. הרבה פעמים אחרי שחווים אירוע מאיים או קשה או במצבים שחוששים מאירועים כאלה חווים קושי או מצוקה. אני רוצה לציין בפניך את העובדה {improvement_description} אם {will_feel} שוב מצוקה. בנוסף אני רוצה לציין כי {you_might} לחוות בהמשך כל מיני קשיים, שהם טבעיים ונורמליים כמו תמונות של מה שקרה או {that_you_afraid} שיקרה, קושי בשינה, ומספר רגשות כמו מצוקה, פחד או כעס. אם {experience} אותם, מומלץ לך להשתמש בתרגול שעשינו.
אם {you_notice} לב שהתגובות האלה לא פוחתות, או נמשכות יותר מ 2-3 ימים, אני {encourage} אותך לפנות לאחד מהגופים הבאים, שיוכלו לעזור לך להתמודד עם התגובות האלו:{contacts}
אני מקווה שסייעתי לך {wish} לך הקלה משמעותית נוספת במצבך""".format(
        improvement_description = improvement_description,
        will_feel = "תחוש" if is_patient_male else "תחושי",
        you_might = "אתה עלול" if is_patient_male else "את עלולה",
        that_you_afraid = "שאתה חושש" if is_patient_male else "שאת חוששת",
        experience = "תחווה" if is_patient_male else "תחווי",
        you_notice = "אתה שם" if is_patient_male else "את שמה",
        encourage = "מעודד" if is_bot_male else "מעודדת",
        contacts = contacts,
        wish = "ומאחל" if is_bot_male else "ומאחלת")

class State:
    def __init__(self, run: Callable, chat_input = ChatInputFreeText):
        self.chat_input = chat_input
        self.run = run

async def write_exit_text(request_context: RequestContext):
    if request_context.get_var(VariableShouldSaveClientStatus):
        entity = {
            "PartitionKey": PartitionKey,
            "RowKey": request_context.get_var(VariableClientId),
            "Status": "finished"
        }
        await request_context.app_resources.table_client.update_entity(mode=UpdateMode.REPLACE, entity=entity)

    request_context.set_next_state(StateEndInput)
    return request_context.write_chat_message(request_context.get_var(VariableExitText))
States[StateExit] = State(chat_input=ChatInputNotWait, run=write_exit_text)

def end_input(request_context: RequestContext):
    return None
States[StateEndInput] = State(chat_input=ChatInputDisabled, run=end_input)