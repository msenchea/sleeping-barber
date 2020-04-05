import threading
import time
import random
import queue # queue get and put are thread safe, excellent module to import.

BARBERS = 3 # set amount of barbers here
CUSTOMERS = 100 # set amount of customers for the day here
SEATS = 15 # set amount of seats in the waiting room here
ARRIVAL_WAIT = 1 # set multiple of random.random() that customers arrive

def arrival_wait(): # simulates customers arriving at random times
	time.sleep(ARRIVAL_WAIT * random.random())

class Barber(threading.Thread):
	condition = threading.Condition() # to put the barber to sleep/wake up
	should_stop = threading.Event() # for when all customers have been serviced

	def __init__(self, ID):
		super().__init__()
		self.ID = ID	# barber ID number


	def run(self):
		while True:
			try:	# using a try & except is better than checking qsize, as queue.qsize() is not thread safe.
				current_customer = waiting_room.get(block=False) # block=false so thread doesn't wait/block for a space in the queue.
			except queue.Empty: # thrown when waiting room is empty.
				if self.should_stop.is_set(): # should_stop is only set after all customers have been processed for the day.
					return

				print(f"barber {self.ID} sleeping") # no customers, sleep
				with self.condition:
					self.condition.wait() # sleep and wait for customer to wake me
			else:
				current_customer.trim(self.ID) # cut the customers hair

class Customer(threading.Thread):
	HAIRCUT_DURATION = 5

	def __init__(self, ID):
		super().__init__()
		self.ID = ID

	def haircut(self): # simulates a haircut
		time.sleep(self.HAIRCUT_DURATION * random.random())

	def trim(self, barber_ID):  # called from Barber thread
		print(f"barber {barber_ID} is cutting customer {self.ID}'s hair")
		self.haircut() # get a haircut
		print(f"barber {barber_ID} finished cutting customer {self.ID}'s hair")
		self.serviced.set() # set serviced so customer may leave the barbershop

	def run(self):
		self.serviced = threading.Event()

		try:	# check if theres space in the waiting room
			waiting_room.put(self, block=False)
		except queue.Full: # no space, leave
			print(f"waiting room full, {self.ID} left")
			return

		print(f"customer {self.ID} sat in waiting room")
		with Barber.condition:
			Barber.condition.notify(1) # wakes up exactly 1 barber if there are any sleeping

		self.serviced.wait() # wait to get haircut and then leave


if __name__ == "__main__":
	all_customers = []          # list of all customers for the day
	waiting_room = queue.Queue(SEATS) # max size of SEATS, removes need to check Queue.qsize() before Queue.put()

	for i in range(BARBERS): # create barber threads
		barber_thread = Barber(i)
		barber_thread.start()

	for i in range(CUSTOMERS): # create customer threads
		arrival_wait()
		customer = Customer(i)
		all_customers.append(customer)
		customer.start()

	for customer in all_customers:
		customer.join()  # wait for all customers to leave

	time.sleep(0.1) # to give the last barber enough time to clean up after the final customer
	Barber.should_stop.set() # let the barbers know work is over for the day
	with Barber.condition:
		Barber.condition.notify_all() # wake them all up if they are sleeping so they can leave

	print("barber shop closed")
