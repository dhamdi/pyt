
import csv

class Recommender:

	RATING_ATTRS = ['service', 'cleanliness', 'value', 'location', 'sleep_quality', 'rooms']

	def __init__(self):
		# dizionario con cui effettuare il parsing delle review contenute nel dataset
		self._reviews = dict()
		# dizionario che conterrà, per ogni utente del dataset, il suo modello.
		# Ogni modello è indicizzato dall'id dell'utente di appartenenza
		self._user_models = dict()
		# dizionario che conterrà, per ogni item del dataset, il suo modello.
		# Ogni modello è indicizzato dall'id dell'item di appartenenza
		self._item_models = dict()

	# dato in input il nome di un attributo contenuto in RATING_ATTRS, restituisce il nome con cui l'attributo è
	# definito nel file csv
	def __get_csv_attribute(self, rating_attr):
			return 'ratings.' + rating_attr


	def __crea_user_models(self):

		# dizionario che conterrà, per ogni utente, il numero di reviews allo stesso associate.
		# I valori sono indicizzati rispetto all'id degli utenti
		num_reviews_utente = dict()
		# dizionario che conterrà, per ogni utente, il numero di voti dallo stesso dati a ciascuna delle
		# dimensioni dei vari item.
		# Ogni elemento di tale dizionario sarà a sua volta un dizionario contenente, per ciascuna dimensione, un contatore
		# indicizzato dal nome della dimensione stessa.
		num_voti_utente = dict()

		# scorro lungo ogni review, per estrapolare i diversi id utente
		for review in self._reviews.values():
			# ricavo l'id dell'utente associato alla review
			user_id = review['author.id']
			# se num_reviews_utente non ha una chiave corrispondente all'id dell'utente, vuol dire che questa è la prima review
			# tra quelle scorse finora che è associata all'utente, quindi inserisco in num_reviews_utente e in num_voti_utente
			# rispettivamente il numero di review e il numero di voti assegnati ad ogni dimensione degli item relativi all'utente stesso,
			# inizializzandoli a 0
			if num_reviews_utente.get(user_id) == None:
				num_reviews_utente[user_id] = 0
				num_voti_utente[user_id] = { rating_attr: 0 for rating_attr in Recommender.RATING_ATTRS }
			# incremento di 1 il numero di review associate all'utente
			num_reviews_utente[user_id] += 1
			# per ogni dimensione dell'item, se l'utente ne ha dato un voto (cioè se la stringa non è vuota), ne incremento il contatore
			for rating_attr in Recommender.RATING_ATTRS:
				if review[self.__get_csv_attribute(rating_attr)]:
					num_voti_utente[user_id][rating_attr] += 1

		# per ogni utente contenuto nel dataset, calcolo il suo livello di interesse per ciascuna dimensione contenuta in RATING_ATTRS, 
		# effettuando una divisione tra il numero di voti da lui dati per quella dimensione nelle sue review e il numero totale di 
		# review da lui effettuate
		for user_id in num_reviews_utente.keys():
			livelli_utente = dict()
			for rating_attr in Recommender.RATING_ATTRS:
				livelli_utente[rating_attr] = round(float(num_voti_utente[user_id][rating_attr]) / int(num_reviews_utente[user_id]), 1)
			self._user_models[user_id] = livelli_utente

	def __crea_item_models(self):

		# dizionario che conterrà, per ogni item, il numero totale dei voti dati dagli utenti a ciascuna dimensione dell'item
		# ogni elemento del dizionario è indicizzato dall'id dell'item
		num_ratings_items = dict()
		# dizionario che conterrà, per ogni item, la somma di tutti i voti dati dagli utenti a ciascuna dimensione dell'item
		# ogni elemento del dizionario è indicizzato dall'id dell'item
		somme_ratings_items = dict()

		# scorro lungo l'insieme delle review
		for review in self._reviews.values():
			# ricavo l'id dell'item relativo alla review corrente
			item_id = review['offering_id']
			# se non è ancora stato creato un elemento indicizzato dall'id dell'item, vuol dire che questa è la prima
			# review relativa a tale item, quindi inserisco nei due dizionari la conta dei voti e la loro somma per ogni
			# dimensione dell'item indicizzandoli con l'id dell'item stesso e inizializzando tali valori a 0
			if num_ratings_items.get(item_id) == None:
				num_ratings_items[item_id] = { rating_attr: 0 for rating_attr in Recommender.RATING_ATTRS }
				somme_ratings_items[item_id] = { rating_attr: 0 for rating_attr in Recommender.RATING_ATTRS }

			# per ogni dimensione dell'item, se la review corrente fornisce un voto per la dimensione stessa, incremento di 1 il numero
			# totale di voti dati all'item per quella dimensione e il valore di tale voto alla loro somma
			for rating_attr in Recommender.RATING_ATTRS:
				if review[self.__get_csv_attribute(rating_attr)]:
					num_ratings_items[item_id][rating_attr] += 1
					somme_ratings_items[item_id][rating_attr] += float(review[self.__get_csv_attribute(rating_attr)])

		# ottenuto, per ogni  ogni item, il numero totale dei voti degli utenti e la loro somma per ogni sua dimensione, 
		# ricavo il modello dell'item stesso, dato dalla media dei voti dati per ogni sua dimensione.
		# Se per un item, una certa dimensione ha ottenuto 0 voti, la media non è computabile, quindi essa sarà posta pari a -1
		for item_id in num_ratings_items.keys():
			medie_voti = dict()
			for rating_attr in Recommender.RATING_ATTRS:
				if num_ratings_items[item_id][rating_attr] > 0:
					medie_voti[rating_attr] = round(somme_ratings_items[item_id][rating_attr] / num_ratings_items[item_id][rating_attr], 1)
				else:
					medie_voti[rating_attr] = 0
			self._item_models[item_id] = medie_voti

	# legge il dataset delle review creando, per ogni item e per ogni utente contenuto nel dataset, il suo modello
	def parse_dataset(self):

		with open("review_tripadvisor_10.csv", encoding="utf-8") as f:
			# reader = csv.reader(f, delimiter=';')
			dictReader = csv.DictReader(f, delimiter=';')
			for review in dictReader:
				self._reviews[review['id']] = review
			
			# 22412
			# print(len(self._reviews))
			# print(not list(self._reviews.values())[2]['ratings.rooms'])

			self.__crea_user_models()
			self.__crea_item_models()


	def get_user_model(self, user_id):
		return self._user_models[user_id].copy()

	def get_item_model(self, item_id):
		return self._item_models[item_id].copy()

	# restituisce l'overall rating inferito di un item da parte di un utente mediante la formula
	# overall_rating = (importanza_1 * valore_medio_1 + (1 - importanza_1)) + 
	# 				   (importanza_2 * valore_medio_2 + (1 - importanza_2)) +
	#				    ... +
	#				   (importanza_N * valore_medio_N + (1 - importanza_N))
	# dove:
	# importanza_i è il valore dell'importanza che la dimensione i-esima ha per l'utente
	# valore_medio_i è il valor medio di tutti i voti che l'item ha per la dimensione i-esima
	def get_recommendation_value(self, user_id, item_id):

		overall_rating = 0
		for rating_attr in Recommender.RATING_ATTRS:
			attr_importance = self._user_models[user_id][rating_attr]
			attr_medium_value = self._item_models[item_id][rating_attr]
			overall_rating += attr_importance * attr_medium_value + (1 - attr_importance)

		return round(overall_rating / len(Recommender.RATING_ATTRS), 1)
		