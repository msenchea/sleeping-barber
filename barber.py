import sys
import threading
import time
import random
import queue

BARBERS = 3 # set amount of barbers here
CUSTOMERS = 10 # set amount of customers for the day here
SEATS = 5 # set amount of seats in the waiting room here

wr_lock = threading.Lock()  # lock for accessing of the waiting room

ARRIVAL_WAIT = 0.01

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
			with self.condition:
				wr_lock.acquire()
				if waiting_room.qsize == 0:
					wr_lock.release()
					#print(f"barber {self.ID} sleeping")
					self.condition.wait() #sleep and wait for customer
				else:
					wr_lock.release()

				if self.should_stop.is_set():
					print(f"barber {self.ID} has signed out for the day")
					return

				wr_lock.acquire()
				if waiting_room.qsize == 0:
					current_customer = waiting_room.get()
					wr_lock.release()
					current_customer.trim(self.ID)
				else:
					wr_lock.release()

class Customer(threading.Thread):
	WAIT = 0.05

	def __init__(self, ID):
		super().__init__()
		self.ID = ID

	def wait(self):
		time.sleep(self.WAIT * random.random())

	def trim(self, barber_ID):  # Called from Barber thread
		# Get a haircut
		#print(f"barber {barber_ID} is cutting customer {self.ID}'s hair")
		self.wait()
		#print(f"customer {self.ID}'s hair is cut.'")
		self.serviced.set()

	def run(self):
		self.serviced = threading.Event()
		# Grab the barbers' attention, add ourselves to the customers,

		wr_lock.acquire()
		if not(waiting_room.qsize() >= waiting_room.maxsize):
			waiting_room.put(self)
			wr_lock.release()
			with Barber.condition:
				Barber.condition.notify(1)
			#print(f"customer {self.ID} took a seat in the waiting room")
		else:
			wr_lock.release()
			print(f"waiting room is full, customer {self.ID} is leaving.")
			return

		while not self.serviced.is_set():
			continue

		print(f"customer {self.ID} is leaving")


if __name__ == "__main__":

	all_customers = []          # list of all customers for the day
	waiting_room = queue.Queue(SEATS)

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
	# Grab the barbers' attention and tell them all that it's time to leave - using conditions I think

	for b in range(BARBERS):
		Barber.should_stop.set()
		with Barber.condition:
			Barber.condition.notify(1)
