#!/usr/bin/env bash
CWD=$(pwd)
SCRIPT=$(realpath "${BASH_SOURCE[0]}")
SCRIPTS_ROOT=$(dirname "${SCRIPT}")
LUNAR_ROOT=$(dirname "${SCRIPTS_ROOT}")
LUNARCORE_NAME="lunarcore"
LUNARCORE_ROOT="${LUNAR_ROOT}/${LUNARCORE_NAME}"

START_CMD=(poetry run "${LUNARCORE_NAME}" start)
STOP_CMD=(poetry run "${LUNARCORE_NAME}" stop)
USER=$(id -un)

pid_file="${LUNAR_ROOT}/${LUNARCORE_NAME}.pid"
log="${LUNAR_ROOT}/${LUNARCORE_NAME}.log"

get_pid() {
    cat "${pid_file}"
}

is_running() {
    [ -f "${pid_file}" ] && ps -p `get_pid` > /dev/null 2>&1
}

wait_for_process() {
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
  do
    if ! is_running; then
      break
    fi
    printf "."
      sleep 1
  done
}

case "$1" in
    start)
    if is_running; then
        printf "%s already started\n" "${LUNARCORE_NAME}"
    else
        printf "Starting %s\n" "${LUNARCORE_NAME}"
        cd "${LUNARCORE_ROOT}"
        if [ -z "${USER}" ]; then
            sudo "${START_CMD[@]}" >> "${log}" 2>&1 &
        else
            sudo -u "${USER}" "${START_CMD[@]}" >> "${log}" 2>&1 &
        fi
        wait_for_process

        echo $! > "${pid_file}"
        if ! is_running; then
            printf "Unable to start, see %s.\n" "${log}"
            exit 1
        fi
        echo "${LUNARCORE_NAME} started successfully." >> "${log}"
    fi
    ;;
    stop)
    if is_running; then
        printf "Stopping %s ...\n" "${LUNARCORE_NAME}"
#        cd "${LUNARCORE_ROOT}"
#        if [ -z "${USER}" ]; then
#            sudo "${STOP_CMD[@]}" >> "${log}" 2>&1 &
#        else
#            sudo -u "${USER}" "${STOP_CMD[@]}" >> "${log}" 2>&1 &
#        fi
        kill "$(get_pid)"

        wait_for_process

        if is_running; then
            printf "%s not stopped; may still be shutting down or shutdown may have failed\n" "${LUNARCORE_NAME}"
            printf "Forcing stop ..."
            kill -9 "$(get_pid)"
        else
            printf "%s stopped\n" "${LUNARCORE_NAME}"

        if [ -f "${pid_file}" ]; then
                rm "${pid_file}"
            fi
        fi
        echo "${LUNARCORE_NAME} stopped successfully." >> "${log}"
    else
        printf "%s not running\n" "${LUNARCORE_NAME}"
    fi
    ;;
    restart)
    $0 stop
    if is_running; then
        printf "Unable to stop %s, will not attempt to start\n" "${LUNARCORE_NAME}"
        exit 1
    fi
    $0 start
    ;;
    status)
    if is_running; then
        printf "%s is running\n" "${LUNARCORE_NAME}"
    else
        printf "%s stopped\n" "${LUNARCORE_NAME}"
        exit 1
    fi
    ;;
    *)
    printf "Usage: %s {start|stop|restart|status}\n" "$0"
    exit 1
    ;;
esac

exit 0