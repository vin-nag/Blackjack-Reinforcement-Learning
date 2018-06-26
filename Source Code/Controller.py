
# Blackjack AI project
# Authors: Steve Parson, Nabil Miri, Vineel Nagisetty
# Made for Final Report of CS 3200 Course, taught by Dr. David Churchill
# Controller class which represents the AI agent

import random
import math
import copy

class Controller:
    """
    Constructor takes:
    model = Model object we will use
    aitype = type of AI used: "MC" (Monte-Carlo), "SARSA", or "QL" (Q Learning)
    action_selector = Either "EPS" (Epsilon-Greedy) or "UCB" (Upper Confidence Bound)
    ai_parameter_1 = Value between 0 and 1. Represents step-size for MC, or alpha value for the other two
    ai_parameter_2 = Value between 0 and 1. Represents Gamma(discount factor) for QL and SARSA, not used by MC
    selector_parameter = Value between 0 and 1. Represents epsilon for epsilon-greedy, or c (exploration constant) for UCB
    num_iterations = the number of games to play
    use_average_update: True or False based on whether to use average update method

    Other attributes:
    Q, P and N represent maps for values, policy, and number of times a state is visited
    mapSize, dealerSize, actions control the size of our maps
    t represents the time-steps
    """
    def __init__(self,
                 model,
                 aitype="MC",
                 action_selector="EPS",
                 ai_parameter_1=0.1,
                 ai_parameter_2=1,
                 selector_parameter=0.15,
                 num_iterations=2500000,
                 use_average_update=True,
                 check_for_convergence=False,
                 verbose=False):

        # Get initial values from Model
        self.last_policymap = []
        self.model = model
        self.AIType = aitype
        self.ActionSelector = action_selector
        self.AIParameter = ai_parameter_1
        self.AIParameter2 = ai_parameter_2
        self.SelectorParameter = selector_parameter
        self.IterationNum = num_iterations
        self.mapSize = 130
        self.dealerSize = 12
        self.stepSize = 0.1
        self.actions = [0, 1, 2]
        self.t = 1
        self.verbose = verbose
        self.useAverageUpdate = use_average_update
        self.checkForConvergence = check_for_convergence

        self.Q = [[[0 for action in range(len(self.actions))] for dealer in range(self.dealerSize)] for player in
                  range(self.mapSize)]

        self.P = [[[1.0 / len(self.actions) for action in range(len(self.actions))] for dealer in range(self.dealerSize)]
                  for hand in range(self.mapSize)]

        self.N = [[[1 for action in range(len(self.actions))] for dealer in range(self.dealerSize)] for player in
                  range(self.mapSize)]

        self.QConverge = [[[1 for action in range(len(self.actions))] for dealer in range(self.dealerSize)]
                  for hand in range(self.mapSize)]

        self.learn()

    def learn(self):
        """
        This function learns the policy, initializing the maps, then plays the given number of games
        :return: None
        """
        for i in range(self.IterationNum):

            # refresh the model to a new game
            self.model.start()

            # exploring starts? (maybe)
            self.model.playerHand.hand_sum = random.randint(2, 21)
            if self.model.playerHand.hand_sum > 11:
                if random.random() < (4 / 52):
                    self.model.playerHand.number_of_aces = 1
            if self.model.playerHand.hand_sum == 2:
                self.model.playerHand.number_of_aces = 2
            if self.model.playerHand.hand_sum == 3:
                self.model.playerHand.number_of_aces = 1

            # print iteration number for every 20,000 iterations
            if i % 20000 == 0:
                if self.verbose:
                    print("i =", i)

                if self.checkForConvergence and self.converged_policy():
                    print("converged at iteration: ", i)
                    break

            episode = self.generate_game()

            if self.AIType == "MC":
                self.update_values_mc(episode)

            self.update_policy(episode)
        return

    def generate_game(self):
        """
        This function creates and plays one game of Black-Jack
        :return: sequence of events for the game in the form of: [state, action, reward]
        """
        episode = []

        # while the game is running
        while self.model.isRunning:

            # state is of the form [playerHand, dealerHand]
            state = self.model.get_state_rl()

            # for QLearning, we pick a random action to take, for the other two, we pick based on the policy
            action = self.select_action_random() if self.AIType == "QL" else self.select_action(state)

            # Update time-steps                                                                                       )
            self.N[state[0]][state[1]][action] += 1
            self.t += 1

            # do the action
            self.model.do_player_action(action)

            # play out dealer turn(s). If our action was stand, continue dealer action until game is done
            while not self.model.playerTurn and self.model.isRunning:
                self.model.do_dealer_action()

            # get reward from the model for our action
            reward = self.model.get_reward()

            # if SARSA or Q-Learning, update Q based on the respective formula
            if self.AIType == "SARSA":
                state_next = self.model.get_state_rl()
                action_next = self.select_action(state_next)
                self.update_values_sarsa(state, action, reward, state_next, action_next)

            elif self.AIType == "QL":
                state_next = self.model.get_state_rl()
                action_next = self.select_action_best(state_next)
                self.update_values_ql(state, action, reward, state_next, action_next)

            # add tuple to the episode array
            episode.append([state, action, reward])

        return episode

    def converged_policy(self):
        """
        This function checks if the policy has converged by checking for difference between Q values at certain steps
        as long as the action has been called atleast 30 times
        :return:
        """
        for player in range(self.mapSize):
            for dealer in range(self.dealerSize):
                for action in range(len(self.actions)):
                    if abs(self.Q[player][dealer][action]-self.QConverge[player][dealer][action])>0.15 \
                            or (self.N[player][dealer][action]<30 and self.N[player][dealer][action]>2):
                        self.QConverge = copy.deepcopy(self.Q)
                        return False
        return True

    def select_action(self, state):
        """
        This function selects an action based on chosen selection method, epsilon-greedy or ucb
        :param state:
        :return:
        """
        action = 0
        if self.ActionSelector == "EPS":
            action = self.select_action_epsilon(state)
        elif self.ActionSelector == "UCB":
            action = self.select_action_ucb(state)
        else:
            print("Wrong Action Selector selected")

        return action

    def select_action_ucb(self, state):
        """
        This function selects an action based on the Upper Confidence Bound method
        forumula: best action = max value of [Q[state][action] + c * sqrt(ln t/Nt(a)) ]

        :param state:
        :return: action
        """
        player_hand = state[0]
        dealer_hand = state[1]
        ucbvalues = [0,0,0]
        max_action_value = -99999
        max_actions = []

        for action in range(len(self.actions)):
            ucbvalues[action] = self.Q[player_hand][dealer_hand][action] + self.SelectorParameter * \
                                math.sqrt(math.log(self.t)/self.N[player_hand][dealer_hand][action])

        for action in range(len(ucbvalues)):
            if max_action_value < self.P[player_hand][dealer_hand][action]:
                max_action_value = self.P[player_hand][dealer_hand][action]

        for action in range(len(ucbvalues)):
            if abs(max_action_value - self.P[player_hand][dealer_hand][action]) < 0.0001:
                max_actions.append(action)

        return random.choice(max_actions)

    def select_action_epsilon(self, state):
        """
        This function selects an action based on the Epsilon-Greedy Method. A random action is chosen less than
        epsilon times, or a greedy action is chosen 1 - e + e/num_actions times
        :param state:
        :return: action
        """
        random_p = random.random()

        if random_p < self.SelectorParameter:
            return self.select_action_random()

        else:
            return self.select_action_best(state)

    def select_action_random(self):
        """
        This function returns a random action from the self.actions
        :return: action
        """
        return random.choice(self.actions)

    def select_action_best(self, state):
        """
        This function selects the best action to take. If multiple best actions, it will choose one at random
        :param state:
        :return: action
        """
        player_hand = state[0]
        dealer_hand = state[1]
        max_action_value = -99999
        max_actions = []

        for action in range(len(self.actions)):
            if max_action_value < self.P[player_hand][dealer_hand][action]:
                max_action_value = self.P[player_hand][dealer_hand][action]

        for action in range(len(self.actions)):
            if abs(max_action_value - self.P[player_hand][dealer_hand][action]) < 0.0001:
                max_actions.append(action)

        return random.choice(max_actions)

    def update_values_sarsa(self, state, action, reward, state_next, action_next):
        """
        This function updates the values array for SARSA using the
        forumula: Q[S][A] = Q[S][A] + α*(R + γ*Q[S’][A’] – Q[S][A])
        :param state:
        :param action:
        :param reward:
        :param state_next:
        :param action_next:
        :return: None
        """
        player_hand = state[0]
        dealer_hand = state[1]
        player_hand_next = state_next[0]
        dealer_hand_next = state_next[1]

        # if we need to use average update rule
        if self.useAverageUpdate:
            self.AIParameter = self.updateTimeStep(player_hand,dealer_hand,action)

        self.Q[player_hand][dealer_hand][action] += \
            self.AIParameter * \
            (reward + self.AIParameter2 *
             self.Q[player_hand_next][dealer_hand_next][action_next] - self.Q[player_hand][dealer_hand][action])

        return

    def update_values_mc(self, episode):
        """
        This function updates the values array for Monte Carlo method using the
        formula: Q[S][A] = Q[S][A] + step size * (Reward - Q[S][A])
        :param episode:
        :return: None
        """
        final_reward = self.model.get_reward()

        for t in range(len(episode)):
            player_hand = episode[t][0][0]
            dealer_hand = episode[t][0][1]
            action = episode[t][1]

            # if we need to use average update rule
            if self.useAverageUpdate:
                self.AIParameter = self.updateTimeStep(player_hand,dealer_hand,action)

            self.Q[player_hand][dealer_hand][action] += self.AIParameter * (
                        final_reward - self.Q[player_hand][dealer_hand][action])

        return

    def update_values_ql(self, state, action, reward, state_next, action_next):
        """
        This function updates the values array for Q-Learning using the
        formula: Q[S][A] = Q[S][A] + α*(R + γ*max_action_Q[S’][a] – Q[S][A])
        :param state:
        :param action:
        :param reward:
        :param state_next:
        :param action_next:
        :return: None
        """
        player_hand = state[0]
        dealer_hand = state[1]
        player_hand_next = state_next[0]
        dealer_hand_next = state_next[1]

        # if we need to use average update rule
        if self.useAverageUpdate:
            self.AIParameter = self.updateTimeStep(player_hand,dealer_hand,action)

        self.Q[player_hand][dealer_hand][action] += self.AIParameter * (
                reward + self.AIParameter2 * self.Q[player_hand_next][dealer_hand_next][action_next] -
                self.Q[player_hand][dealer_hand][action])

        return

    def update_policy(self, episode):
        """
        This function updates the policy for either of the methods. It sets the best action policy to 1/num_best_actions
        and other policies to 0
        :param episode:
        :return: None
        """
        for t in range(len(episode)):

            max_actions = []
            max_action_value = -99999
            player_hand = episode[t][0][0]
            dealer_hand = episode[t][0][1]

            for action in range(len(self.actions)):
                if max_action_value < self.Q[player_hand][dealer_hand][action]:
                    max_action_value = self.Q[player_hand][dealer_hand][action]

            for action in range(len(self.actions)):
                if abs(max_action_value - self.Q[player_hand][dealer_hand][action]) < 0.0001:
                    max_actions.append(action)

            self.P[player_hand][dealer_hand] = [0, 0, 0]

            for action in max_actions:
                self.P[player_hand][dealer_hand][action] = 1.0/len(max_actions)

        return

    def updateTimeStep(self, player_hand, dealer_hand, action):
        """
        This function returns the value for step size for when the average update rule is selected
        :param state:
        :return:
        """
        return 1/(self.N[player_hand][dealer_hand][action])
