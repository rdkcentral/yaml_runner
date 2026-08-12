#** *****************************************************************************
# *
# * If not stated otherwise in this file or this component's LICENSE file the
# * following copyright and licenses apply:
# *
# * Copyright 2024 RDK Management
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *
# http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *
#* ******************************************************************************
"""Takes a list of commands and runs them."""
import io
import subprocess
import sys
import threading

from .models import CompletedCommand

def run_commands(commands: list[str], fail_fast: bool) -> list[CompletedCommand]:
    """
    Runs a list of commands in the self.commands attribute and returns the completed commands.

    Returns:
        A list of CompletedCommands
    """
    completed_commands = []

    for command in commands:
        completed_command = _run_command(command)
        completed_commands.append(completed_command)
        if fail_fast and completed_command.exit_code > 0:
            break
    return completed_commands

def _run_command(command: str) -> CompletedCommand:
    """Runs a command in the shell, captures both stdout and stderr,
    prints them in real-time, and returns them.

    Args:
        command: A list containing the command and its arguments.

    Returns:
        A tuple containing captured stdout (bytes) and stderr (bytes).
    """
    stdout_result = []
    stderr_result = []
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    ) as proc:
        stdout_thread = threading.Thread(target=_read_stream,
                                            args=(proc.stdout, 'stdout',stdout_result))
        stderr_thread = threading.Thread(target=_read_stream,
                                            args=(proc.stderr, 'stderr', stderr_result))

        stdout_thread.start()
        stderr_thread.start()
        # Wait for the process to finish
        return_code = proc.wait()
        # Ensure threads finish reading and collect data
        stdout_thread.join()
        stderr_thread.join()

    return CompletedCommand(return_code, stdout_result[0], stderr_result[0])

def _read_stream(stream:io.IOBase, target:str, result_list:list):
    """Read data from a stream and writes it to either stdout or stderr whilst also
    capturing the data.

    Args:
        stream (io.IOBase): Stream object from which data will be read.
        target (str): Where the output from the stream should be directed. Either 'stdout' or 'stderr'
        result_list (list): The list that will store the data read from the stream.
            Each chunk of data read from the stream will be appended to this list.
    """
    data = ''
    if target == 'stdout':
        output = sys.stdout
    elif target == 'stderr':
        output = sys.stderr

    while True:
        chunk = stream.readline()
        if chunk == '':
            break
        data += chunk
        output.write(chunk)
        output.flush()
    result_list.append(data)