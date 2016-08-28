from collections import defaultdict
from collections import OrderedDict
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

#Server type with various sizes
server = [("large", 1), 
		  ("xlarge", 2), 
		  ("2xlarge", 4), 
		  ("4xlarge", 8), 
		  ("8xlarge", 16), 
		  ("10xlarge", 32)
		 ]



class ResourceAllocator:
	'''
		Resource alocator module class
	'''

	def __init__(self):
		'''Init'''

		self.cpuWithQuantity = []
		self.cpuTotalCost = 0
		self.returnVal = {}
		self.finalResult = []
		self.server = server
		self.maxCycleChecked = True

	def get_costs(self, instances, hours = 1, cpus = 0, price = 0):
		'''Doc - get costs of server'''
		
		self.instances = instances
		self.hours = hours
		self.cpus = cpus
		self.price = float(price)
		self.cpuQty = 0

		for region , v in self.instances.items():
			self.returnVal["region"] 		= region
			self.returnVal["servers"]		= self.getServers(region,v)
			self.returnVal["total_cost"] 	= locale.currency(self.cpuTotalCost)
			self.finalResult.append(self.returnVal)
			self.returnVal = {}
	
		return self.finalResult

	def getServers(self, region, cpuWithCost):
		'''
			Gets the server qunaity and generating cpu cost
		'''
		self.cpuQty = 0
		self.cpuWithQuantity = []
		while self.cpuQty < self.cpus:
			for serverType, serverCpuQty in reversed(self.server):
				self.getCpuQuantity(serverType, serverCpuQty, region)

		if (self.price and not self.cpus):
			self.getCpuForGivenPrice(region)

		return self.getAggregateCpuQty()	

	def getCpuForGivenPrice(self, region):
		'''
			Gets the cpu qunaity for an given hours and price
		'''
		self.maxCycleChecked = True

		while self.cpuTotalCost <= self.price and self.maxCycleChecked:
			count = 0
			updatedCost = self.cpuTotalCost
			for serverType, serverCpuQty in reversed(self.server):
				try:
					if (serverType in self.instances[region]):
						curcpuQty = self.cpuQty + serverCpuQty
						if (self.cpuTotalCost <= self.price):
							self.cpuQty = curcpuQty						
							serverCost = self.instances[region][serverType]
							self.cpuWithQuantity.append((str(serverType), (serverCpuQty, serverCost)))
							count += 1
				except Exception as error:
					print(error)
			
			self.getAggregateCpuQty()
			if (count == 0 or self.cpuTotalCost == updatedCost):
				self.maxCycleChecked= False


	def getCpuQuantity(self, serverType, serverCpuQty, region):
		'''
			Returns the server type, CPU quanity, with price 
		'''
		if (self.cpus):
	
			try:
				if (serverType in self.instances[region]):
					curcpuQty = self.cpuQty + serverCpuQty
					if (curcpuQty <= self.cpus):
						self.cpuQty = curcpuQty						
						serverCost = self.instances[region][serverType]
						self.cpuWithQuantity.append((str(serverType), (serverCpuQty, serverCost)))
					else:
						pass
			except Exception as error:
				print(error)	
	

	def getAggregateCpuQty(self):
		'''
			Returns aggregated server with sum of qty
		
		'''
		self.cpuTotalCost = 0
		qtyOfCpu = defaultdict(int)
		for k, i in self.cpuWithQuantity:
			if (self.price != 0):
				if (self.cpuTotalCost < self.price):
					self.cpuTotalCost += self.hours * i[1]
					qtyOfCpu[k] += i[0]
					if (self.cpuTotalCost > self.price):
						self.cpuTotalCost -=self.hours * i[1]
						qtyOfCpu[k] -= i[0]
						self.maxCycleChecked = False
			else:
				self.cpuTotalCost += i[1]
				qtyOfCpu[k] += i[0]

		if (self.hours and self.hours!= 1 and self.price == 0):
			self.cpuTotalCost = self.hours * self.cpuTotalCost 
		return qtyOfCpu.items()

