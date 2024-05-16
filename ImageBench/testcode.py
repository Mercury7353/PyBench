 
import cv2
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Load the image
image = cv2.imread('./data/34.png')

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use thresholding to create a binary image
_, binary_image = cv2.threshold(gray_image, 120, 255, cv2.THRESH_BINARY)

# Prepare the wordcloud text
text = "AI, AGI, LLM, Agent, CodeInterpreter, Code, Visualization"

# Create the wordcloud
wordcloud = WordCloud(width=800, height=800, background_color='white', mask=binary_image).generate(text)

# Save the wordcloud image
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('./output/34_wordcloud.png')
