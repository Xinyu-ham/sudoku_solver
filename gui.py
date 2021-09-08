from selenium import webdriver
from sudoku_solver import Grid
import numpy as np
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import time
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--difficulty',  default=4)
parser.add_argument('--depth',  default=5)
parser.add_argument('--choices',  default=2)

args = parser.parse_args()

difficulty = args.difficulty
d = int(args.depth)
c = int(args.choices)
url = f'https://nine.websudoku.com/?level={difficulty}'

chrome = webdriver.Chrome('chromedriver')
chrome.maximize_window()
chrome.get(url)

#wait to load
time.sleep(2)
elements = chrome.find_elements_by_xpath("//input[@class='s0']")
values = [[int(e.get_attribute('value')), int(e.get_attribute('id')[1]), int(e.get_attribute('id')[2])] for e in elements]

grid = np.zeros([9, 9])
for v in values:
    grid[v[2]][v[1]] = v[0]

grid = Grid(grid)
ans = grid.recur_solve(max_depth=d)

output = chrome.find_elements_by_xpath("//input[@class='d0']")
print(ans)
for e in output:
    i, j = int(e.get_attribute('id')[2]), int(e.get_attribute('id')[1])
    if ans[i][j] != 0:
        print(i, j, ans[i][j])
        e.send_keys(str(ans[i][j]))





