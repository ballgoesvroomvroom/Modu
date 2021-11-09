import time
import json
import random

class GenerationError(Exception):
	def __init__(self, msg):
		super().__init__(msg)

class utils():
	def IntToStr(n: int):
		"""
		Returns the time (in xhymin format) from an integer (minutes)
		"""
		## n = 43; returns 43min
		## n = 128; returns 2hr 8min
		hour, minute = n // 60, n % 60
		if hour == 0:
			return "{}min".format(minute)
		elif minute == 0:
			return "{}hr".format(hour)
		else:
			return "{}hr {}min".format(hour, minute)

	def GetElapsedSinceZero(s: str):
		"""
		Return the duration in minutes that has passed sicne 00:00
		"""
		## s = 08:00
		c = s.split(":")
		if len(c) != 2:
			raise GenerationError("Invalid input of %s, > 1 colons detected"%(s))

		hour, minute = c
		if len(hour) != 2 or len(minute) != 2:
			raise GenerationError("Invalid input, malformed fields in hh:mm, %s"%(s))

		return int(hour) *60 + int(minute)

class ParamObject():
	def __init__(self):
		self.Seed = -1
		self.Start = "08:00"
		self.End = "18:00"
		self.Periods = {"ProjectA": [1, 50, 50], "ProjectB": [2, 25, 25]}
		self.SetInPlace = {"ProjectC's meeting": ["10:00", "11:00", "14:00", "15:00"]}

	def AddPeriod(self, name, frequency, bottomtimelimit, uppertimelimit):
		"""
		Adds the period to self.Periods
		"""
		self.Periods[name] = [frequency, bottomtimelimit, uppertimelimit]

	def RemovePeriod(self, name):
		"""
		Removes the period in self.Periods
		"""
		if name in self.Periods:
			del self.Periods[name]

	def AddSetInPlace(self, name, start_timing, end_timing):
		"""
		Adds a period to self.SetInPlace
		"""
		if name in self.SetInPlace:
			self.SetInPlace[name].append(start_timing)
			self.SetInPlace[name].append(end_timing)
		else:
			self.SetInPlace[name] = [start_timing, end_timing]

	def RemoveSetInPlace(self, name):
		"""
		Removes a period in self.SetInPlace
		"""
		if name in self.SetInPlace:
			del self.SetInPlace[name]

	def Purge(self, periodName):
		"""
		Removes all instances of the period
		"""
		if periodName in self.Periods: del self.Periods[periodName]
		if periodName in self.SetInPlace: del self.SetInPlace[periodName]

	def Clean(self):
		"""
		Removes all periods
		"""
		self.Periods = {}
		self.SetInPlace = {}

class Schedule():
	def __init__(self, params):
		if len(params.Periods) == 0:
			raise GenerationError("There cannot be zero periods")
		elif type(params) != ParamObject:
			raise GenerationError("Params passed must the type ParamObject")

		self.g_start = utils.GetElapsedSinceZero(params.Start) ## minutes
		self.start = 0 ## relative
		self.end = self.__GetElapsedSinceStart(params.End)
		if params.Seed == -1:
			self.seed = random.randint(1, 1000)/1000
		else:
			self.seed = params.Seed
		random.seed(a = self.seed)

		if self.start > self.end:
			raise GenerationError("Start time cannot be later than end time")

		self.duration = self.end -self.start

		self.periods = []

		## check for duplicates in Periods
		registered = []
		for setted_per in params.Periods:
			if setted_per in registered:
				raise GenerationError("Cannot have duplicate periods in .Periods")
			registered.append(setted_per)

		## take into account of the SetInPlace
		remaining_dur = self.duration ## store the duration remaining after added set in place periods
		for setted_per in params.SetInPlace:
			data = params.SetInPlace[setted_per]
			if len(data) % 2 != 0:
				raise GenerationError("SetInPlace for period: %s, does not contain enough start and end points"%(setted_per))
			for i in range(0, len(data), 2):
				start = self.__GetElapsedSinceStart(data[i])
				end = self.__GetElapsedSinceStart(data[i +1])
				if start > end:
					raise GenerationError("SetInPlace for period: %s, does not contain a valid start and end group, with start > end"%(setted_per))
				remaining_dur -= (end -start)
				self.periods.append([setted_per, start, end, end -start])
		self.write_json("output.json")
		self.__sort() ## sort self.periods in order and check for overlapping of periods

		if len(self.periods) >= 1:
			if self.periods[0][1] < self.start:
				## check if first period is within the start range
				raise GenerationError("Earlierst period in SetInPlace, %s, starts before set range"%(self.periods[0][0]))
			elif self.periods[-1][2] > self.end:
				## check if the latest period in SetInPlace ending time before self.end
				raise GenerationError("Latest period in SetInPlace, %s, ends after set range"%(self.periods[-1][0]))


		## split remaining_dur into the periods with the given ratio
		total_units = 0
		for period in params.Periods:
			period_datagroup = params.Periods[period]
			if type(period_datagroup[0]) != int and type(period_datagroup[0]) != float:
				raise GenerationError("Ratio can only be a number")
			if type(period_datagroup[1]) != int or type(period_datagroup[2]) != int:
				raise GenerationError("Bottom and upper bounds for period can only be positive (not zeroes too) whole numbers")
			elif period_datagroup[1] <= 0 or period_datagroup[2] <= 0:
				raise GenerationError("Bottom and upper bounds for period can only be positive (not zeroes too) whole numbers")
			elif period_datagroup[1] > period_datagroup[2]:
				raise GenerationError("Bottm bound cannot be greater than upper bound")
			total_units += period_datagroup[0]

		time_per_period = {}
		total_time_taken = 0 ## might be lesser than remaining_dur, need to assign extra time to a random period
		for period in params.Periods:
			time_taken = int(params.Periods[period][0]/total_units *remaining_dur) ## remaining_dur is in minutes

			total_time_taken += time_taken
			time_per_period[period] = time_taken
		## handle excess time
		if remaining_dur > total_time_taken:
			## usually only larger by a small amount since we round down values
			for x in time_per_period:
				time_per_period[x] += (remaining_dur - total_time_taken)
				break ## add the excess time to one period
		## add in periods
		curr_timepointer = self.start +1
		curr_period = None ## put the current period trying to slot in here
		curr_period_len = 0
		push = False ## push current period into schedule
		# print(time_per_period)
		while curr_timepointer <= self.end:
			occupied = False
			occupied_index = 0
			for period in self.periods:
				if curr_timepointer >= period[1] and curr_timepointer < period[2]:
					## within range of another period's instance's start and end time
					occupied = True
					break
				occupied_index += 1
			# print(curr_timepointer, occupied, curr_period, curr_period_len, push)
			if (occupied and curr_period != None) or push:
				## push current period instance into self.periods
				start = curr_timepointer -curr_period_len
				end = curr_timepointer

				if occupied:
					curr_timepointer = self.periods[occupied_index][2] +1 ## skip to the end of the occupied period slot
				elif push:
					## just a simple push, no occupancy was detected, no need to jump to end of period
					## curr_timepointer += 1
					pass

				if push:
					## need to find position of the current period
					occupied_index = 0
					for period in self.periods:
						if occupied_index >= 1:
							if start >= self.periods[occupied_index -1][2] and end <= self.periods[occupied_index][1]:
								break
						else:
							if end <= self.periods[0][1]:
								break
						occupied_index += 1
				self.periods.insert(occupied_index, [curr_period, start, end, end -start])

				time_per_period[curr_period] -= (end -start)

				## reset to default values
				curr_timepointer -= 1
				curr_period = None
				curr_period_len = 0
				push = False
			elif occupied and curr_period == None:
				curr_timepointer = self.periods[occupied_index][2] ## skip to the end of the occupied period slot
			elif not occupied and curr_period != None:
				curr_period_len += 1

				time_limit = params.Periods[curr_period] ## index 1 and 2
				random_stoplimit = random.randint(time_limit[1], time_limit[2]) ## bottom and upper bounds
				# random_stoplimit_a = (random_stoplimit // 5) * 5
				# print(random_stoplimit, random_stoplimit_a)
				if curr_period_len > time_per_period[curr_period] or curr_period_len > time_limit[2] or curr_period_len >= random_stoplimit or curr_timepointer == self.end:
					push = True
				else:
					pass

				curr_timepointer += 1
			elif not occupied and curr_period == None:
				## select a random period
				random_period = ""

				banned = []
				while random_period == "" and len(banned) < len(time_per_period):
					## get random period to fill in gap
					## it should never run out of periods to use
					y, t = random.choice(list(time_per_period.items()))
					if y in banned:
						continue
					elif t > 0:
						random_period = y
					else: banned.append(y)
				if len(banned) == len(time_per_period):
					raise GenerationError("INTERNAL ERROR")

				curr_period = random_period
				curr_period_len = 0

				# curr_timepointer += 1 ## no need to increase, increase it only at the next iteration since we're assigning data to this curr_timepointer
		self.__sort() ## redundant as it should have been sorted
		self.__merge()
		self.__convert()
		##self.write_json("output.json")

	def __repr__(self):
		start_time = self.__GetElapsedTimeSinceStartFromMinutes(self.start)
		end_time = self.__GetElapsedTimeSinceStartFromMinutes(self.end)
		r = " {} - {} {:>17}".format(start_time, end_time, "Seed: " +str(self.seed))
		for period in self.periods:
			name = period[0]
			start = period[1]
			end = period[2]
			dur = utils.IntToStr(period[3])

			left_margin = "{:^7}".format(start) ## store time header
			toadd = "{}| {:<15} | {}".format(left_margin, name, dur)
			r += "\n" + toadd + "\n" + "-" *len(left_margin) + "|" + "-" *(15 +2) + "|" + "-" *(len(dur) +1)
		return r


	def write_json(self, filename):
		"""
		Writes self.periods into filename
		"""
		with open(filename, "w") as f:
				f.write(json.dumps(self.periods, indent = 4))

	def rwrite(self, filename):
		"""
		Writes itself, converted by repr(), into filename
		"""
		with open(filename, "w") as f:
			f.write(repr(self))

	def __GetElapsedSinceStart(self, s: str):
		"""
		Gets the elapsed time (in minutes) since self.g_start
		"""
		## s = 08:10
		global_elapsed = utils.GetElapsedSinceZero(s)
		return global_elapsed -self.g_start ## global start, self.start is in relative mode, hence it is zero and is useless
	def __GetElapsedTimeSinceStartFromMinutes(self, s: str):
		"""
		Gets the elapsed time (in hh:mm format) since self.g_start
		"""
		## s = 10
		total_time = self.g_start + int(s)
		hour, minute = total_time // 60, total_time % 60
		return "%02d:%02d"%(hour, minute)
	def __merge(self):
		"""
		Modify and merge adjacent periods that are the same
		"""
		p = self.periods
		curr_pointer = 0
		while curr_pointer < len(p) -1: ## minus one because we dont need curr_pointer to reach the last element
			if p[curr_pointer][0] == p[curr_pointer +1][0]:
				## remove p[curr_pointer] but also swap p[curr_pointer]'s end time with p[curr_pointer +1]'s end time 
				## also update the duration value
				p[curr_pointer][2] = p[curr_pointer +1][2]
				p[curr_pointer][3] = p[curr_pointer][2] -p[curr_pointer][1]
				del p[curr_pointer +1]
			else:
				curr_pointer += 1 ## only increment if no merging was done
	def __convert(self):
		"""
		Converts elements in self.periods from elapsed time in minutes to a readable string, in "hh:mm" format
		"""
		for c, period in enumerate(self.periods):
			for i in range(1, 3):
				self.periods[c][i] = self.__GetElapsedTimeSinceStartFromMinutes(self.periods[c][i])
	def __sort(self):
		"""
		Sorts self.periods; start and end
		Implementation of selection sort?
		"""
		p = self.periods

		for x in range(len(p)):
			smallest_index = x ## make the first element of the unsorted list the smallest_index
			for y in range(x, len(p)):
				if p[y][1] < p[smallest_index][1]:
					smallest_index = y
			p[x], p[smallest_index] = p[smallest_index], p[x]
			if x > 0:
				## check if periods overlap
				prev = p[x -1]
				if prev[2] > p[x][1]:
					## previous period ended after current period starts; overlap
					raise GenerationError("%s overlaps with %s"%(prev[0], p[x][0]))
		## modifies self.periods; no need to return anything