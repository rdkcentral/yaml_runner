#!/usr/bin/env python3
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

from os import path
import sys

MY_PATH = path.abspath(__file__)
MY_DIR = path.dirname(MY_PATH)

# This is to allow this script to run without pip installing yaml_runner
sys.path.append(path.join(MY_DIR,'../src'))
from yaml_runner import YamlRunner

if __name__ == '__main__':
    YAML_RUNNER = YamlRunner()
    sys.exit(YAML_RUNNER.run()[2][0])
