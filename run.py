import ScheduleGen

paramobj = ScheduleGen.ParamObject()
schedule = ScheduleGen.Schedule(paramobj)
print(schedule)
schedule.rwrite("output.txt")
schedule.write_json("output.json")