#!/bin/bash
SHELL_FOLDER=$(cd `dirname ${0}`; pwd)
cd ${SHELL_FOLDER}/../

function patchroom()
{
    GAMEID=$1
    svn --no-auth-cache --username tuyoobuild --password tuyougame revert  game/${GAMEID}/room/*.json
    svn --no-auth-cache --username tuyoobuild --password tuyougame up      game/${GAMEID}/room/
    pypy ${SHELL_FOLDER}/room_${GAMEID}.py
}

patchroom 6
patchroom 7
patchroom 17

