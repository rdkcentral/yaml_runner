#!/usr/bin/env bash

function _get_config_arg()
{
	local args=("$@")
	local count=0
	for word in "${args[@]}"
	do
		if [[ '-c' == "${word}" || '--config' == "${word}" ]]; then
			((count++))
			if [[ -f "${args[$count]}" ]];then
				_YR_CONF="${args[$count]}"
			fi
			return
		fi
		((count++))
	done
}

function _yaml_runner_completion()
{
	unset _YR_CONF
	_get_config_arg "${COMP_WORDS[@]}"
	local IFS='
	'
	if [[ -n "${_YR_CONF:-}" ]]; then
 		COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
 					COMP_CWORD=$COMP_CWORD \
 					_YAML_RUNNER_COMPLETE=complete_bash $1 --config "${_YR_CONF}" ) )
 	else
 		COMPREPLY=()
 	fi
	return 0
}

complete -o default -F _yaml_runner_completion yaml_runner
