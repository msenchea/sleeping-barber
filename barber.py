import threading
import time
import random
import queue

BARBERS = 3 # set amount of barbers here
CUSTOMERS = 1000 # set amount of customers for the day here
SEATS = 15 # set amount of seats in the waiting room here
ARRIVAL_WAIT = 0.01 # set multiple of random.random() that customers arrive

def wait():
	time.sleep(ARRIVAL_WAIT * random.random())

class Barber(threading.Thread):
	condition = threading.Condition()
	should_stop = threading.Event() #for when all customers have been serviced

	def __init__(self, ID):
		super().__init__()
		self.ID = ID


	def run(self):
		while True:
			try:
				current_customer = waiting_room.get(block=False)
			except queue.Empty:
				if self.should_stop.is_set():
					print(f"barber {self.ID} has signed out for the day")
					return

				print(f"barber {self.ID} sleeping")
				with self.condition:	# prevents sleep-awake cycle
					self.condition.wait() #sleep and wait for customer
			else:
				current_customer.trim(self.ID)

class Customer(threading.Thread):
	WAIT = 0.05

	def __init__(self, ID):
		super().__init__()
		self.ID = ID

	def wait(self):
		time.sleep(self.WAIT * random.random())

	def trim(self, barber_ID):  # Called from Barber thread
		# Get a haircut
		print(f"barber {barber_ID} is cutting customer {self.ID}'s hair")
		self.wait()
		print(f"barber {barber_ID} finished cutting customer {self.ID}'s hair")
		#print(f"customer {self.ID}'s hair is cut.'")
		self.serviced.set()

	def run(self):
		self.serviced = threading.Event()
		# Grab the barbers' attention, add ourselves to the customers,

		try:
			waiting_room.put(self, block=False) # block=False makes it so put doesn't wait for a space in the queue.
		except queue.Full: # Prevents me from needing to use a lock.
			print(f"waiting room full, {self.ID} left")
			return

		print(f"customer {self.ID} sat in waiting room")
		with Barber.condition:
			Barber.condition.notify(1)
			#print(f"customer {self.ID} took a seat in the waiting room")

		self.serviced.wait()

		#print(f"customer {self.ID} is leaving")


if __name__ == "__main__":

	all_customers = []          # list of all customers for the day
	waiting_room = queue.Queue(SEATS) #Max size of SEATS takes care not needing to check qsize before Queue.put()

	for i in range(BARBERS):
		barber_thread = Barber(i)
		barber_thread.start()
		#print(f"barber {i} started")	# using fstrings as they are easier to read than formatting - must have python 3.6 or above installed however.

	for i in range(CUSTOMERS):
		wait()
		customer = Customer(i)
		all_customers.append(customer)
		customer.start()
		#print(f"customer {i} started")

	for customer in all_customers:
		customer.join()  # Wait for all customers to leave
	# Grab the barbers' attention and tell them all that it's time to leave

	Barber.should_stop.set()
	with Barber.condition:
		Barber.condition.notify_all()
