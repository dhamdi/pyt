
from recommender import Recommender 

r = Recommender()
r.parse_dataset()
# r._Recommender__print_item_models_with_no_medium_values()

user_id = '1BBD0A79D3F59310BF1E27B1A1AAA2C2'
item_id = '1762573'
print("user_model: " + str(r.get_user_model(user_id)))
print("item_model: " + str(r.get_item_model(item_id)))
print("recommended value: " + str(r.get_recommendation_value(user_id, item_id)))