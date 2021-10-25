import ScheduleGen

paramobj = ScheduleGen.ParamObject()
paramobj.Clean()

paramobj.Start = "14:00"
paramobj.End = "21:00"

paramobj.AddPeriod("grind money", 3, 20, 60)
paramobj.AddPeriod("be a nerd", 2, 40, 60)
paramobj.AddPeriod("leisure", 1, 25, 30)

paramobj.AddSetInPlace("Food", "14:30", "15:00")
paramobj.AddSetInPlace("YouDownloader", "14:00", "14:30")
paramobj.AddSetInPlace("YouDownloader", "15:00", "16:00")

schedule = ScheduleGen.Schedule(paramobj)
schedule.rwrite("output.txt")
##schedule.write_json("output.json")
print(schedule)
input()