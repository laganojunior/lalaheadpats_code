from PIL import Image
import numpy as np
import math
import sys

p = float(sys.argv[1])

w = 1024
h = 1024

prize_zero_game = 0
prize_one_game = 20
prize_two_game = 200
prize_three_game = 400

gradient_range = 50
gradient_buckets = 5

image_data = np.zeros((h, w, 3), dtype=np.uint8)

def get_min_prob_less_than_t(dist1_val, dist2_val):
    return dist1_val + dist2_val - dist1_val * dist2_val

def get_max_prob_less_than_t(dist1_val, dist2_val):
    return dist1_val * dist2_val

def get_winner_prob_less_than_t(dist1_val, dist2_val, p):
    return p * get_max_prob_less_than_t(dist1_val, dist2_val) + (1-p) * get_min_prob_less_than_t(dist1_val, dist2_val)

def get_expected_tickets(skill_lesser_than_probs, p):
    game_1_p = p * skill_lesser_than_probs[0] + (1-p) * (1 - skill_lesser_than_probs[0])
    game_2_p = p * skill_lesser_than_probs[1] + (1-p) * (1 - skill_lesser_than_probs[1])
    game_3_p = p * skill_lesser_than_probs[2] + (1-p) * (1 - skill_lesser_than_probs[2])

    return prize_zero_game * (1 - game_1_p) + \
           prize_one_game * game_1_p * (1 - game_2_p) + \
           prize_two_game * game_1_p * game_2_p * (1 - game_3_p) + \
           prize_three_game * game_1_p * game_2_p * game_3_p

def get_expected_tickets_first_round(x, y, p):
    # Face jon first
    game_1_opp_skill_less_than_x = 1 
    game_2_opp_skill_less_than_x = get_winner_prob_less_than_t(x, x, p)
    game_3_opp_skill_less_than_x = get_winner_prob_less_than_t(get_winner_prob_less_than_t(x, x, p), get_winner_prob_less_than_t(x, x, p), p)

    expected_tickets_x = get_expected_tickets([game_1_opp_skill_less_than_x, game_2_opp_skill_less_than_x, game_3_opp_skill_less_than_x], p)

    game_1_opp_skill_less_than_y = 0
    game_2_opp_skill_less_than_y = get_winner_prob_less_than_t(y, y, p)
    game_3_opp_skill_less_than_y = get_winner_prob_less_than_t(get_winner_prob_less_than_t(y, y, p), get_winner_prob_less_than_t(y, y, p), p)

    expected_tickets_y = get_expected_tickets([game_1_opp_skill_less_than_y, game_2_opp_skill_less_than_y, game_3_opp_skill_less_than_y], p)

    return expected_tickets_x + expected_tickets_y

def get_expected_tickets_final_round(x, y, p):
    game_1_opp_skill_less_than_x = x
    game_2_opp_skill_less_than_x = get_winner_prob_less_than_t(x, x, p)
    game_3_opp_skill_less_than_x = get_winner_prob_less_than_t(get_winner_prob_less_than_t(1, x, p), get_winner_prob_less_than_t(x, x, p), p)

    expected_tickets_x = get_expected_tickets([game_1_opp_skill_less_than_x, game_2_opp_skill_less_than_x, game_3_opp_skill_less_than_x], p)

    game_1_opp_skill_less_than_y = y
    game_2_opp_skill_less_than_y = get_winner_prob_less_than_t(y, y, p)
    game_3_opp_skill_less_than_y = get_winner_prob_less_than_t(get_winner_prob_less_than_t(0, y, p), get_winner_prob_less_than_t(y, y, p), p)

    expected_tickets_y = get_expected_tickets([game_1_opp_skill_less_than_y, game_2_opp_skill_less_than_y, game_3_opp_skill_less_than_y], p)

    return expected_tickets_x + expected_tickets_y

def get_gradient_color(gradient_value):
    yellow = [255, 242, 0]
    red = [255, 0, 0]
    green = [31, 150, 0]

    if gradient_value >= 0:
        # Yellow to green
        return [
            yellow[0] + (green[0] - yellow[0]) * gradient_value,
            yellow[1] + (green[1] - yellow[1]) * gradient_value,
            yellow[2] + (green[2] - yellow[2]) * gradient_value,
        ]
    else:
        # Yellow to red
        return [
            yellow[0] + (red[0] - yellow[0]) * -gradient_value,
            yellow[1] + (red[1] - yellow[1]) * -gradient_value,
            yellow[2] + (red[2] - yellow[2]) * -gradient_value,
        ]

# Create Image
img_filename = f'graph_p_{p}.png'
print(f"Making {img_filename}")

for i in range(h):
    y =  1.0 - (i + 1) / h

    for j in range(w):
        x = j / w

        expected_tickets_first_round = get_expected_tickets_first_round(x, y, p)
        expected_tickets_final_round = get_expected_tickets_final_round(x, y, p)

        if y >= x:
            pixel = [255, 255, 255]
        else:
            diff = expected_tickets_final_round - expected_tickets_first_round

            
            if diff >= gradient_range:
                gradient_bucketed_value = 1.0
            elif diff <= -gradient_range:
                gradient_bucketed_value = -1.0
            else:
              gradient_value = diff / gradient_range
              gradient_bucket = round(gradient_value * gradient_buckets)
              gradient_bucketed_value = gradient_bucket * (1.0 / gradient_buckets)


            pixel = get_gradient_color(gradient_bucketed_value)

        # Grid
        if (abs(x - round(x, 1)) < 0.001) or (abs(y - round(y, 1)) < 0.001):
            pixel = [125, 125, 125]

        image_data[i, j] = pixel

image = Image.fromarray(image_data, 'RGB')
image.save(img_filename)