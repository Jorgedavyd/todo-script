#!/bin/bash

if [[ -n $1 && -n $2 && -n $3 ]]; then
    project_path=$1
    obsidian_vault_path=$2
    filepath=$3
    python3 todo-script/on_written.py --filepath "$filepath" --obsidian_vault_path "$obsidian_vault_path" --project_path "$project_path"
    exit 0
fi

if [[ -n $1 && -n $2 ]]; then
    project_path=$1
    obsidian_vault_path=$2
    python3 todo-script/whole_project.py --obsidian_vault_path "$obsidian_vault_path" --project_path "$project_path"
    exit 0
fi

echo 'Not valid parameters'
exit 1

