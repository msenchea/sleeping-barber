import sys
import threading
import time
import random

BARBERS = 1 # set amount of barbers here
CUSTOMERS = 20 # set amount of customers for the day here
SEATS = 5 # set amount of seats in the waiting room here

ARRIVAL_WAIT = 0.01

waiting_room_lock = threading.Lock()

def wait():
	time.sleep(ARRIVAL_WAIT * random.random())

class Barber(threading.Thread):

	is_asleep = False

	def is_sleeping(self):
		return self.is_asleep

	def sleep(self):
		pass
		self.is_asleep = True

	def wake_up(self):
		pass

	def cut_hair(self, customer):
		time.sleep(random.random())
		# customer.set() or something
		pass

	def run(self):
		should_stop = threading.Event()

		while True:
			waiting_room_lock.acquire()
			if not waiting_room.is_empty():
				customer = waiting_room.next()
				waiting_room_lock.release()
				self.cut_hair(customer)
			else:
				waiting_room_lock.release()
				self.sleep()


class Customer(threading.Thread):

	def run(self):
		hair_cut = threading.Event()
		while not hair_cut:
			pass
	def go_to_waiting_room(self):
		waiting_room_lock.acquire()
		if waiting_room.is_full():
			waiting_room_lock.release()
			time.sleep()
		else:
			waiting_room.join_queue(self)
			waiting_room_lock.release()


class WaitingRoom():

	def __init__(self, seats):
		self.queue = []
		self.seats = seats

	def is_empty(self):
		return len(self.queue) == 0

	def is_full(self):
		return len(self.queue) == self.seats

	def join_queue(self, customer):
		self.queue.append(customer)

	def next(self):
		next = self.queue[0]
		del self.queue[0]
		return next


if __name__ == "__main__":
	all_customers = []          # list of all customers for the day
	barbers = []

	waiting_room = WaitingRoom(20)
	print("waiting room initialised")

	for b in range(BARBERS):
		b = Barber()
		barbers.append(b)
		b.start()

	for c in range(CUSTOMERS):
		wait()
		c = Customer()
		all_customers.append(c)
		c.start()
		print("customer started")

	for c in all_customers:
		c.join()  # Wait for all customers to leave
	# Grab the barbers' attention and tell them all that it's time to leave - using events I think
	print("The shop is now closed.")