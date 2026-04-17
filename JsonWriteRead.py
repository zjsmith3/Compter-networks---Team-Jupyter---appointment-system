import json
from datetime import datetime

#opening the save file for the functions to use. 
with open("doctorAppointmentsSaveFile.json", "r") as f:
    saveFile = json.load(f)

def getDoctorList():
    return list(saveFile.keys())

def getDoctorMonths(doctor):

    if doctor not in saveFile:
        return []

    return list(saveFile[doctor].keys())


def getMonthDays(doctor, month):

    if doctor not in saveFile:
        return []

    if month not in saveFile[doctor]:
        return []

    return list(saveFile[doctor][month].keys())

def getTimeSlots(doctor, month, day):

    if doctor not in saveFile:
        return []

    if month not in saveFile[doctor]:
        return []

    if day not in saveFile[doctor][month]:
        return []


    available = []
    for time, value in saveFile[doctor][month][day].items():
        if value is None:
            available.append(time)
    return available

def getTodayTimeSlots(doctor):
    today = datetime.today()
    month = today.strftime("%B")
    day = str(today.day)

    if doctor not in saveFile:
        return []

    if month not in saveFile[doctor]:
        return []

    if day not in saveFile[doctor][month]:
        return []

    available = []
    for time, value in saveFile[doctor][month][day].items():
        if value is None:
            available.append(time)
    return available

def isTimeSlotAvailable(doctor, month, day, time):
    return saveFile[doctor][month][day][time] is None

def bookAppointment(doctor, month, day, time, bookingInfo):
    
    saveFile[doctor][month][day][time] = bookingInfo

    with open("doctorAppointmentsSaveFile.json", "w") as writingSaveFile:
        json.dump(saveFile, writingSaveFile, indent=4)

if __name__ == "__main__":
    print("temp")
    # print(getTodayTimeSlots("John Doe"))
    
    # for doctor in getDoctorList():
    #     print(doctor)
    # for month in getDoctorMonths("Jane Doe"):
    #     print(month)
    # for day in getMonthDays("Jane Doe", "April"):
    #     print(day)
    # for timeslot in getTimeSlots("Jane Doe", "April", "10"):
    #     print(timeslot)