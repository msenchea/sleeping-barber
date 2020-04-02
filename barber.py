import sys
import threading
import time
import random

BARBERS = 1 # set amount of barbers here
CUSTOMERS = 20 # set amount of customers for the day here
SEATS = 5 # set amount of seats in the waiting room here

ARRIVAL_WAIT = 0.01

def wait():
	time.sleep(ARRIVAL_WAIT * random.random())

class Barber(threading.Thread):
	condition = threading.Condition()
	customers = []
	should_stop = threading.Event() #for when all customers have been serviced

	def run(self):
		while True:
			with self.condition:
				if not self.customers:
					print("barber sleeping")
					self.condition.wait() #sleep and wait for customer
				current_customer = self.customers[0]
			current_customer.trim()

			if self.should_stop.is_set():
				break



class Customer(threading.Thread):
	WAIT = 0.05
	def wait(self):
		time.sleep(self.WAIT * random.random())

	def trim(self):  # Called from Barber thread
		# Get a haircut
		print("customer is getting a haircut")
		self.serviced.set()


	def run(self):
		self.serviced = threading.Event()
		# Grab the barbers' attention, add ourselves to the customers,
		barbers[0].condition.notify()
		barbers[0].customers.append(self)
		print("waiting to be serviced")
		while not self.serviced.is_set():
			continue


		# and wait to be serviced


if __name__ == "__main__":
	all_customers = []          # list of all customers for the day
	barbers = []            # list of all barbers

	for b in range(BARBERS):
		wait()
		b = Barber()
		barbers.append(b)
		b.start()
		print("barber started")

	for c in range(CUSTOMERS):
		wait()
		c = Customer()
		all_customers.append(c)
		c.start()
		print("customer started")

	for c in all_customers:
		c.join()  # Wait for all customers to leave
	# Grab the barbers' attention and tell them all that it's time to leave - using events I think
	barbers[0].should_stop.set()