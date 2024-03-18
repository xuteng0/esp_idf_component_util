import os
import sys
import json

_task_label = "Create New Component"

## Add task to VSCode tasks.json


def _vscode_tasks_read():
    tasks_file_path = os.path.join('.vscode', 'tasks.json')
    if os.path.isfile(tasks_file_path):
        with open(tasks_file_path, 'r') as file:
            return json.load(file)
    return {"version": "2.0.0", "tasks": [], "inputs": []}


def _vscode_tasks_write(tasks_config):
    os.makedirs('.vscode', exist_ok=True)
    with open(os.path.join('.vscode', 'tasks.json'), 'w') as file:
        json.dump(tasks_config, file, indent=4, sort_keys=True)


def _vscode_task_add(task_label):
    new_task = {
        "label": task_label,
        "type": "shell",
        "command": "python3",
        "args": [
            "${workspaceFolder}/util.py", "new-component",
            "${input:componentName}"
        ],
        "problemMatcher": [],
        "group": {
            "kind": "build",
            "isDefault": True
        }
    }
    new_input = {
        "id": "componentName",
        "description": "Enter the name of the new component:",
        "type": "promptString"
    }

    tasks_config = _vscode_tasks_read()
    if not any(task for task in tasks_config["tasks"] if task["label"] == task_label):
        tasks_config["tasks"].append(new_task)
        print(f"Task '{task_label}' added to VSCode tasks.json.")
    else:
        print(f"Task '{task_label}' already exists in VSCode tasks.json.")

    if not any(inp for inp in tasks_config.get("inputs", []) if inp["id"] == "componentName"):
        tasks_config.setdefault("inputs", []).append(new_input)
    else:
        print("Input 'componentName' already exists in VSCode tasks.json.")

    _vscode_tasks_write(tasks_config)


def _vscode_task_remove(task_label):
    tasks_config = _vscode_tasks_read()

    # Initial counts for tasks and inputs to determine if removals occur
    initial_task_count = len(tasks_config["tasks"])
    initial_input_count = len(tasks_config.get("inputs", []))

    # Remove the task if it exists
    tasks_config["tasks"] = [task for task in tasks_config["tasks"] if task.get("label") != task_label]

    # Optionally remove the input if it's no longer needed
    tasks_config["inputs"] = [inp for inp in tasks_config.get("inputs", []) if inp.get("id") != "componentName"]

    # Write the updated tasks configuration if any removals occurred
    if len(tasks_config["tasks"]) < initial_task_count or len(tasks_config.get("inputs", [])) < initial_input_count:
        _vscode_tasks_write(tasks_config)
        print(f"Task '{task_label}' and its inputs have been removed from VSCode tasks.json.")
    else:
        print(f"Task '{task_label}' does not exist in VSCode tasks.json.")

    _vscode_tasks_write(tasks_config)
    print(f"Task '{task_label}' removed from VSCode tasks.json.")


def vscode_task_setup():
    task_label = _task_label
    _vscode_task_add(task_label)
    print(f"Setup action completed for task '{task_label}'.")


def vscode_task_cleanup():
    task_label = _task_label
    _vscode_task_remove(task_label)
    print(f"Cleanup action completed for task '{task_label}'.")


## Create new component


def _create_component_dir(component_name, full_directory_path):
    os.makedirs(os.path.join(full_directory_path, "inc"), exist_ok=True)
    os.makedirs(os.path.join(full_directory_path, "private_inc"),
                exist_ok=True)
    os.makedirs(os.path.join(full_directory_path, "src"), exist_ok=True)


def _create_component_cmakelists(component_name, full_directory_path):
    cmake_lists_content = f"""\
# Set source files
set({component_name}_SOURCES
    src/{component_name}.cpp
)

# Set public include directories
set({component_name}_PUBLIC_INCLUDE_DIRS "inc")

# Set private include directories
set({component_name}_PRIVATE_INCLUDE_DIRS "private_inc")

# Set required components
set({component_name}_REQUIRES
)

# Register the component
idf_component_register(
    SRCS ${{{component_name}_SOURCES}}
    INCLUDE_DIRS ${{{component_name}_PUBLIC_INCLUDE_DIRS}}
    PRIV_INCLUDE_DIRS ${{{component_name}_PRIVATE_INCLUDE_DIRS}}
    REQUIRES ${{{component_name}_REQUIRES}}
)
"""
    with open(os.path.join(full_directory_path, "CMakeLists.txt"),
              "w") as file:
        file.write(cmake_lists_content)


def _create_component_cpp(component_name, full_directory_path):
    cpp_content = f"""\
#include "{component_name}.h"
#include "_{component_name}.h"

// Your code here
"""
    with open(
            os.path.join(full_directory_path, "src", f"{component_name}.cpp"),
            "w") as cpp_file:
        cpp_file.write(cpp_content)


def _create_component_pub_h(component_name, full_directory_path):
    h_content = f"""\
#pragma once

#ifdef __cplusplus
extern "C" {{
#endif

// Your declarations here

#ifdef __cplusplus
}}
#endif
"""
    with open(os.path.join(full_directory_path, "inc", f"{component_name}.h"),
              "w") as h_file:
        h_file.write(h_content)


def _create_component_priv_h(component_name, full_directory_path):
    private_h_content = f"""\
// Private header for {component_name}
// Only for use within this component
"""
    with open(
            os.path.join(full_directory_path, "private_inc",
                         f"_{component_name}.h"), "w") as private_h_file:
        private_h_file.write(private_h_content)


def _create_component_source_files(component_name, full_directory_path):
    _create_component_cpp(component_name, full_directory_path)
    _create_component_pub_h(component_name, full_directory_path)
    _create_component_priv_h(component_name, full_directory_path)


def create_component(component_name):
    project_root = os.getcwd()  # Get the current working directory

    # Check if the script is run from the project root by looking for a "main/" directory
    if not os.path.exists(os.path.join(project_root, "main")):
        print(
            "Error: This script must be run from the project root directory (where 'main/' is located)."
        )
        sys.exit(1)  # Exit the script with an error status

    components_dir = os.path.join(project_root, "components")

    # Check if the "components" directory exists, if not, create it
    if not os.path.exists(components_dir):
        os.makedirs(components_dir, exist_ok=True)

    # Construct the full path to the new component directory within "components"
    full_directory_path = os.path.join(components_dir, component_name)

    # Create the directory structure
    _create_component_dir(component_name, full_directory_path)

    # Write the CMakeLists.txt file
    _create_component_cmakelists(component_name, full_directory_path)

    # Create the source files (.cpp, .h, _*.h)
    _create_component_source_files(component_name, full_directory_path)

    print(
        f"Component {component_name} created successfully in {full_directory_path}."
    )


## Main menu


def print_menu():
    print("\nPlease choose an option by entering the corresponding number:")
    print("1. Create a new ESP-IDF component")
    print("2. Setup VSCode tasks.json to add the component creation task")
    print("3. Cleanup VSCode tasks.json and remove the component creation task")
    print("4. Exit")

def main():
    # Check if any command-line arguments were passed
    if len(sys.argv) > 1:
        # Handle direct function calls based on the first argument
        command = sys.argv[1]
        if command == "new-component" and len(sys.argv) == 3:
            component_name = sys.argv[2]
            create_component(component_name)
            return  # Exit after handling the command
        elif command == "setup-vscode-tasks":
            vscode_task_setup()
            return  # Exit after handling the command
        elif command == "cleanup-project":
            vscode_task_cleanup()
            return  # Exit after handling the command
        else:
            print("Invalid command or wrong number of arguments.")
            sys.exit(1)
    
    # If no arguments were passed, fall back to the interactive menu
    try:
        while True:
            print_menu()
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                component_name = input("Enter the name of the new component: ").strip()
                create_component(component_name)
            elif choice == "2":
                vscode_task_setup()
            elif choice == "3":
                vscode_task_cleanup()
            elif choice == "4":
                print("Exiting.")
                break
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nOperation canceled by user. Exiting.")

if __name__ == "__main__":
    main()
