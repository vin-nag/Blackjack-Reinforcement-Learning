# A Comparison Of Reinforcement Learning Algorithms Using Blackjack #


![Game Screenshot](https://github.com/htmlboss/blackjack/blob/master/Report/samplegame.png "In-game UI")

## Table of Contents
* Introduction
* Usage
* Report

## Introduction
In this project, we aim to develop an optimal playing strategy
for the popular game Blackjack. The game is commonly
played at casinos worldwide. The rules are straightforward
and it serves as an interesting model to compare reinforcement
learning algorithms. Which reinforcement learning
algorithm produces the best results with minimal parametric
tweaking? This is the question that we aim to answer.

## Usage

### Windows
* A pre-built `.exe` of the Blackjack game, which is retrieving from the static policies generated can be found in the `python/dist/` directory.
* For the enterprising individual, the build files are in the `python` directory. They are: `Blackjack.spec`, and `CreateInstaller.bat`.

### Source Code
* The model of the game is found in the `python/` directory in the `Model.py` file. 
* The view generated is found in the `python/` directory in the `View.py` file.
* The AI agent is found in the `python/` directory in the `Controller.py` file. 

### Reproduce Results
* To reproduce the results shown in the report, please execute the `ResultDataWriter.py` file, and input your choice of parameters.
* The results of the execution will be found in the `results.csv` file.

## Report
The final report for this project is found [here](https://github.com/htmlboss/blackjack/blob/master/Report/report.pdf).
