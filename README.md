The tools used for this include:
- Flask app
- Celery module for tasks
- Rabbitmq for task queueing

server.py: Runs the flask application
client.py: Example for submitting tasks to the server. It reads from the column in the excel file and generates the number of tasks based on number of rows.
task.py: The task module using celery. This runs separately from flask app.

In order to replicate the setup:
1. Have rabbitmq installed and running
2. Run the flask app: server.py
3. In a separate terminal in the same folder as task.py, run the command: celery -A task worker --loglevel=info --pool=solo
4. Run client.py