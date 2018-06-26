# Blackjack AI project
# Authors: Steve Parson, Nabil Miri, Vineel Nagisetty
# Made for Final Report of CS 3200 Course, taught by Dr. David Churchill
# View class, which creates the model view

import pygame
import Model
import pickle
import sys, os


if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
     os.chdir(sys._MEIPASS)

# load the policy maps
pol_idx = 0
pol_maps = []
pol_files = ['MonteCarlo', 'SARSA', 'QL']
pol_act = ["H", "S", "D"]
for policy_file in pol_files:
    with open(os.path.join("assets", "policies", policy_file + ".dat"), "rb") as f:
        p = pickle.load(f)
    pol_maps.append(p)

# tick counter
tick = 0

m = Model.Model()
running = True

# setup pygame
pygame.init()
pygame.display.set_caption("Blackjack")
f = pygame.font.Font(os.path.join("assets", "fonts", "LiberationSerif-Regular.ttf"), 35)
f2 = pygame.font.Font(os.path.join("assets", "fonts", "CourierNew.ttf"), 15)
s = pygame.display.set_mode((1366, 768))
c = pygame.time.Clock()


while running:
    tick += 1

    # if it's not the player's turn, play out dealer hand
    if not m.playerTurn:
        m.do_dealer_action()

    # for each event in the game
    for event in pygame.event.get():

        # if user wants to quit, let them
        if event.type == pygame.QUIT:
            running = False

        # capture keypress
        if event.type == pygame.KEYDOWN:

            # restart game
            if event.key == pygame.K_r:
                m.start()

            # quit game
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False

            # hit, stand, double down
            if event.key == pygame.K_h and m.playerTurn:
                m.do_player_action(0)
            if event.key == pygame.K_s and m.playerTurn:
                m.do_player_action(1)
            if event.key == pygame.K_d and m.playerTurn:
                m.do_player_action(2)

            # switch policies
            if event.key == pygame.K_p and m.playerTurn:
                pol_idx = (pol_idx + 1) % len(pol_files)

    # print player and dealer values
    player = f.render("Player is: " + str(m.playerHand.get_value()), False, (255, 255, 255))
    dealer = f.render("Dealer is: " + str(m.dealerHand.get_value()), False, (255, 255, 255))

    # load background
    s.blit(pygame.image.load(os.path.join("assets", "felt-bg.jpg")), (0, 0))

    # visualize policy table

    # get the appropriate state number for the policy
    player_policy_value = m.playerHand.get_value() + (100 if m.playerHand.number_of_aces > 0 else 0)

    # print policy map headers
    header = f2.render("Dealer's Upcard", False, (255, 255, 255), (0, 128, 0))
    header2 = f2.render("2  3  4  5  6  7  8  9  T  A", False, (255, 255, 255), (0, 128, 0))
    s.blit(header, (800, 0))
    s.blit(header2, (800, 20))

    # dump the policy for player states 2 through 21 corresponding the dealer 2 through 12
    for player_val in range(2, 22):
        # print player state
        s.blit(f2.render(str(player_val), False, (255, 255, 255), (0, 128, 0)), (760, player_val * 20))

        # print all dealer values in row
        for dealer_val in range(2, 12):
            # figure out best action
            best_action = 0
            for action_idx in range(0, len(pol_maps[pol_idx][player_val][dealer_val])):
                if pol_maps[pol_idx][player_val][dealer_val][action_idx] > pol_maps[pol_idx][player_val][dealer_val][best_action]:
                    best_action = action_idx

            # flash background on best action
            text_background = (128 + (120 * (tick % 2)), 0, 0) if (player_val == player_policy_value and dealer_val == m.dealerHand.get_value()) else (0,20,0)
            s.blit(f2.render(pol_act[best_action], False, (255, 255, 255), text_background), (746 + 27 * dealer_val, player_val * 20))

    # analogous to above, except 112 represents a 12 with a useable ACE
    for player_val in range(112, 122):
        s.blit(f2.render("A"+str(player_val-100), False, (255, 255, 255), (0, 128, 0)), (760, 200+(player_val-100) * 20))
        for dealer_val in range(2, 12):
            best_action = 0
            for action_idx in range(0, len(pol_maps[pol_idx][player_val][dealer_val])):
                if pol_maps[pol_idx][player_val][dealer_val][action_idx] > pol_maps[pol_idx][player_val][dealer_val][best_action]:
                    best_action = action_idx
            text_background = (128 + (120 * (tick % 2)), 0, 0) if (player_val == player_policy_value and dealer_val == m.dealerHand.get_value()) else (0,20,0)
            s.blit(f2.render(pol_act[best_action], False, (255, 255, 255), text_background), (746 + 27 * dealer_val, 200 + (player_val - 100) * 20))

    # draw player cards
    for player_val in range(len(m.playerHand.hand)):
        s.blit(pygame.image.load(os.path.join("assets", m.playerHand.hand[player_val] + ".png")), (300 + 50 * player_val, 0))

    # draw dealer card
    for player_val in range(len(m.dealerHand.hand)):
        s.blit(pygame.image.load(os.path.join("assets", m.dealerHand.hand[player_val] + ".png")), (300 + 50 * player_val, 250))

    # scores and status line
    s.blit(player, (10, 0))
    s.blit(dealer, (10, 250))

    # if the game is over, say so
    if m.isRunning is False:
        s.blit(f.render("Game over, reward=" + str(m.get_reward()), False, (255, 255, 255)), (10, 600))

    # print keypress menu
    status = f.render(
        "[Q]uit [H]it [S]tand [D]oubleDown Change[P]olicy: " + pol_files[pol_idx] + " [R]estart Game",
        False, (255, 255, 255))
    s.blit(status, (10, 700))

    # update the display
    pygame.display.flip()

    # run at 10 fps so that we see animations
    c.tick(10)

pygame.quit()
