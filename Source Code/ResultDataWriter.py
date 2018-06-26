# Blackjack AI project
# Authors: Steve Parson, Nabil Miri, Vineel Nagisetty
# Made for Final Report of CS 3200 Course, taught by Dr. David Churchill
# quick and dirty csv result generator used to generate report data
# no input validation

import Model
import Controller
import time

# create a csv
csv_file_path = "results.csv"
csv = open(csv_file_path, "a")
csv.write("\"Log started: " + str(time.ctime()) + "\"\n")

# instantiate a model object
m = Model.Model()

# get the ai parameters
lower_bound = int(input("How many iterations to start: "))
upper_bound = int(input("How many iterations to stop: "))
iteration_step = input("Iteration step operator: * or +: ")
iteration_step_amount = int(input("Iteration step argument: "))
aitype = input("MC, SARSA, or QL: ")
action_selector = input("EPS or UCB: ")
ai_parameter_1 = float(input("MC step size / Alpha-value: "))

if (aitype == "SARSA" or aitype=="QL"):
    ai_parameter_2 = float(input("Discount factor"))
else:
    ai_parameter_2 = 0

selector_parameter = float(input("Epsilon value if EPS, otherwise UCB-C value: "))
use_average_update = True if input("Use average update? (Y/N): ").upper()=="Y" else False
total_games = int(input("Total games to run at each step: "))

# write the ai parameters to the csv
csv.write(
                "\"aitype: " + str(aitype) +
                ", action_selector: " + str(action_selector) +
                ", lower_bound: " + str(lower_bound) +
                ", upper_bound: " + str(upper_bound) +
                ", iteration_step: " + str(iteration_step) +
                ", iteration_step_amount: " + str(iteration_step_amount) +
                ", ai_parameter_1: " + str(ai_parameter_1) +
                ", ai_parameter_2: " + str(ai_parameter_2) +
                ", selector_parameter: " + str(selector_parameter) +
                ", use_average_update: " + str(use_average_update) +
                ", games played:  " + str(total_games) + "\"\n")
csv.write("\"Iterations\", \"Loss Rate\"\n")

# generate and test policy
while lower_bound <= upper_bound:
    print("Testing the policy that came from  ", lower_bound, " iterations")
    csv.close()
    csv = open(csv_file_path, "a")
    wins = lose = draw = total = 0
    csv.write(str(lower_bound))

    # instantiate an ai object
    c = Controller.Controller(model=m,
                                  aitype=aitype,
                                  action_selector=action_selector,
                                  num_iterations=lower_bound,
                                  ai_parameter_1=ai_parameter_1,
                                  ai_parameter_2=ai_parameter_2,
                                  selector_parameter=selector_parameter,
                                  use_average_update=use_average_update,
                                  check_for_convergence=True,
                                  verbose=True)

    # play total_games number of games
    for game_number in range(total_games):
        # add this game to the total
        total += 1
        # refresh the model
        m.start()
        while True:
            # get the action list
            action_list = c.P[m.get_state_rl()[0]][m.get_state_rl()[1]]

            # get the highest action
            max_action = 0
            for i in range(0, len(action_list)):
                if action_list[i] > action_list[max_action]:
                    max_action = i
            # do the best action
            m.do_player_action(max_action)

            # if it's the dealers turn play it out
            while not m.playerTurn and m.isRunning:
                m.do_dealer_action()

            # if the game is over, break
            if not m.isRunning:
                break

            # add result to running total
        if m.get_reward() > 0:
            wins += 1
        if m.get_reward() == 0:
            draw += 1
        if m.get_reward() < 0:
            lose += 1

    # record the loss percentage
    csv.write(", " + str(lose / total) + "\n")

    # increment the number of iterations of the ai
    if iteration_step == "*":
        lower_bound *= iteration_step_amount
    elif iteration_step == "+":
        lower_bound += iteration_step_amount
csv.write("\n")

# dump the policy table
action_strings = ["H", "S", "D"]
csv.write("*Soft Table*\n")
csv.write("\t\tDealer's Upcard\n")
csv.write("\t2 3 4 5 6 7 8 9 T A\n")
for i in range(113, 122):
    csv.write(str(i - 100) + "\t")
    for j in range(2, 12):
        action, val = max(enumerate(c.Q[i][j]), key=lambda x: x[1])
        csv.write(action_strings[action] + " ")
    csv.write("\n")
csv.write("\n")

csv.write("*Hard Table*\n")
csv.write("\t\tDealer's Upcard\n")
csv.write("\t2 3 4 5 6 7 8 9 T A\n")
for i in range(2, 22):
    csv.write(str(i) + "\t")
    for j in range(2, 12):
        action, val = max(enumerate(c.Q[i][j]), key=lambda x: x[1])
        csv.write(action_strings[action] + " ")
    csv.write("\n")

csv.write("Log ended: " + str(time.ctime()))
csv.write("\"\n")
csv.close()
