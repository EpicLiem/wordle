# way too many hard-coded values for this to be useful as a docker container
# Use the official Python 3.13 image as the base
FROM python:3.13

# Set the working directory in the container
WORKDIR /wordlebot

# Install the dependencies (too lazy to make a requirements.txt)
RUN pip install tqdm

# Copy the rest of your application code
COPY fiveLetterWords.txt fiveLetterWords.txt
COPY wordlebot.py wordlebot.py
# Expose the port your application will listen on
EXPOSE 8000

# Command to run your application
CMD ["python", "wordlebot.py"]