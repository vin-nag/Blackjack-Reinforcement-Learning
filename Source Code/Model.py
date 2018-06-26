# Blackjack AI project
# Authors: Steve Parson, Nabil Miri, Vineel Nagisetty
# Made for Final Report of CS 3200 Course, taught by Dr. David Churchill
# Model class creates a Blackjack game with simplified rules

import random

##############################################################################
# HAND CLASS                                                                 #
##############################################################################
class Hand:
    """ This class represents a hand of cards in Blackjack """
    suit = ['H', 'S', 'D', 'C']
    card = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'K', 'Q', 'A']

    def __init__(self):
        """ Constructor """
        self.hand = []
        self.hand_sum = 0
        self.number_of_aces = 0
        self.first_value = 0
        self.terminal_hand = False
        self.bust = False
        self.double_down = False
        return

    def debug_hand(self):
        """ Print debugging output """
        print("Hand     " + str(self.hand))
        print("Value    " + str(self.get_value()))
        print("Aces     " + str(self.number_of_aces))
        print("Terminal " + str(self.is_terminal_hand()))
        print("Bust     " + str(self.is_bust()))

    def update_sum(self, card):
        """
        Update the current hand's sum
        :param card: the array index from 'card' being added
        """
        # if the index number is less than 8, just add two to it to get the
        # appropriate value
        if card < 8:
            self.hand_sum += int(card) + 2

        # if it's the 12th index, it's an ace
        elif card == 12:
            self.hand_sum += 11

        # otherwise it's a 10, J, K, or Q, all with values of 10
        else:
            self.hand_sum += 10

        # if we have busted, see if we have an ace that we can use
        while self.hand_sum > 21 and self.number_of_aces > 0:
            self.hand_sum -= 10
            self.number_of_aces -= 1

        # if this hand is bust, mark it as a bust terminal hand
        if self.hand_sum > 21:
            self.bust = True
            self.terminal_hand = True

    def add_card(self, number_of_cards, suit_index=None, card_index=None):
        """
        Add a card to a hand
        :param number_of_cards: how many cards to add to the hand
        :param suit_index: optionally choose the first card's suit
        :param card_index: optionally choose the first card
        """

        for i in range(0, number_of_cards):

            # if a card isn't specified, choose an index randomly
            if suit_index is None or card_index is None:
                suit_index = random.randint(0, len(self.suit) - 1)
                card_index = random.randint(0, len(self.card) - 1)

            # if it's an ace, record it
            if self.card[card_index] == 'A':
                self.number_of_aces += 1

            # add the card's representation to the hand list
            self.hand.append((self.suit[suit_index] + self.card[card_index]))

            # update the sum counter
            self.update_sum(card_index)

            # specify the next card as random
            suit_index = card_index = None

            # if this is the first card, record its value
            if len(self.hand) == 1:
                self.first_value = self.get_value()

    def set_terminal_hand(self):
        """ Sets the hand as no longer actionable"""
        self.terminal_hand = True

    def set_double_down(self):
        """ Set a hand to be 'doubled-down' """
        self.double_down = True

    def is_bust(self):
        """ This returns true if a hand is bust """
        return self.bust

    def is_21(self):
        """ Return true if the hand's value is 21 """
        return self.hand_sum == 21

    def is_terminal_hand(self):
        """ Returns true is a hand is no longer actionable """
        return self.terminal_hand

    def is_double_down(self):
        """ Returns true is a hand is doubled down """
        return self.double_down

    def get_value(self):
        """ Returns the integer sum of a hand """
        return self.hand_sum

##############################################################################
# MODEL CLASS                                                                #
##############################################################################
class Model:
    """ This class is our model of the game Blackjack """

    def __init__(self):
        """ Constructor """
        # model is running and it's currently the player's turn
        self.isRunning = True
        self.playerTurn = True

        # create hand for dealer and player
        self.dealerHand = Hand()
        self.playerHand = Hand()

        # add one card for the dealer, and two for the dealer
        self.dealerHand.add_card(1)
        self.playerHand.add_card(2)

    def start(self):
        """ Reinitializes the model """
        self.isRunning = True
        self.playerTurn = True
        self.dealerHand = Hand()
        self.playerHand = Hand()
        self.dealerHand.add_card(1)
        self.playerHand.add_card(2)

    def do_player_action(self, action):
        """
        Does one player action
        :param action: 0 means hit, 1 means stand, 2 means double-down
        """
        # should not have called do_player_action
        if not self.isRunning or self.playerHand.is_bust() or not self.playerTurn:
            return

        # hit
        if action == 0:
            self.playerHand.add_card(1)

        # stand
        elif action == 1:
            self.playerHand.set_terminal_hand()

        # double down
        elif action == 2:
            self.playerHand.add_card(1)
            self.playerHand.set_double_down()
            self.playerHand.set_terminal_hand()

        # if player hand is bust, it's a terminal hand
        # and the game is over
        if self.playerHand.is_bust():
            self.playerHand.set_terminal_hand()
            self.isRunning = False

        # if it's a terminal hand, then end the turn
        if self.playerHand.is_terminal_hand():
            self.playerTurn = False

    def do_dealer_action(self):
        """ Do one dealer action """
        # caller shouldnt have called do_dealer_action
        if self.playerTurn or not self.isRunning or self.dealerHand.is_bust():
            return

        # if this is the first action, always hit to emulate one face down card
        if len(self.dealerHand.hand) == 1:
            self.dealerHand.add_card(1)

        # hit on <17 or soft 17
        elif self.dealerHand.get_value() < 17 or (self.dealerHand.number_of_aces > 0 and self.dealerHand.get_value==17):
            self.dealerHand.add_card(1)
            if self.dealerHand.is_bust():
                self.dealerHand.set_terminal_hand()
                self.isRunning = False

        # otherwise stand
        else:
            self.dealerHand.set_terminal_hand()
            self.isRunning = False

    def get_reward(self):
        """
        Calculate and return the reward associated with this game state
        :return: 0 if draw or game is still active, +1 player win, -1 dealer win
        returns are doubled if player has 'doubled-down'
        """

        # reward is 0 unless in terminal state
        if self.isRunning:
            return 0

        # draw
        if self.playerHand.is_21() and self.dealerHand.is_21():
            return 0

        # natural pays 1.5
        if self.playerHand.is_21():
            return 1.5 * (2 if self.playerHand.is_double_down() else 1)

        # dealer has a natural
        if self.dealerHand.is_21():
            return -1 * (2 if self.playerHand.is_double_down() else 1)


        # player wins
        if self.dealerHand.is_bust():
            return 1 * (2 if self.playerHand.is_double_down() else 1)

        # dealer wins
        if self.playerHand.is_bust():
            return -1 * (2 if self.playerHand.is_double_down() else 1)

        # dealer wins
        if self.dealerHand.get_value() > self.playerHand.get_value():
            return -1 * (2 if self.playerHand.is_double_down() else 1)

        # player wins
        if self.dealerHand.get_value() < self.playerHand.get_value():
            return 1 * (2 if self.playerHand.is_double_down() else 1)

        # default is draw
        return 0

    def get_state_rl(self):
        """ Get the game state representation for the RL algorithm """

        player_element = self.playerHand.get_value() \
            + (100 if self.playerHand.number_of_aces > 0 else 0)

        dealer_element = self.dealerHand.first_value
        return [player_element, dealer_element]
