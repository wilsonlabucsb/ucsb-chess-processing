import os
import subprocess
import time

job_file_path = "job_file.txt"


def mark_command_as_completed(command, status="[COMPLETED]"):
    # Read the existing contents of the job file
    with open(job_file_path, "r") as job_file:
        lines = job_file.readlines()

    # Flag to check if the command is already marked as completed
    command_already_completed = False

    # Replace the line with the completed command
    with open(job_file_path, "w") as job_file:
        for line in lines:
            if command in line:
                # Check if the command is already marked as completed
                if "[COMPLETED]" not in line:
                    # Replace the status of the matching line
                    line = "{command} {status}\n".format(command=command, status=status)
                    command_already_completed = True
            job_file.write(line)

    # If the command is not already marked as completed, append it
    if not command_already_completed:
        with open(job_file_path, "a") as job_file:
            job_file.write("{command} {status}\n".format(command=command, status=status))
        
def run_commands_from_job_file():
    while True:
        print("Checking for commands in the queue...")

        # Read the job file and store commands in a list
        with open(job_file_path, "r") as job_file:
            commands = [line.strip() for line in job_file.readlines()]

        # Execute commands one by one
        for command in commands:
            # Skip completed commands
            if "[COMPLETED]" not in command:
                print("Running command: {command}".format(command=command))

                # Mark the command as running
                mark_command_as_completed(command, status="[RUNNING]")

                process = subprocess.Popen(command.split(), shell=False)
                process.wait()  # Wait for the process to finish before proceeding

                # Optionally, you can check the process return code or handle errors here

                # Mark the command as completed
                mark_command_as_completed(command)

        # Adjust the interval based on your needs
        time.sleep(10)

if __name__ == "__main__":

    # Start running commands from the job file
    run_commands_from_job_file()
