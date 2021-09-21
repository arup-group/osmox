#!/usr/bin/env bash

pushd "${0%/*}"/..

flake8 . --max-line-length 120 --count --show-source --statistics --exclude=scripts,tests,osmread

return_code=$?

popd

# text colours
PLAIN='\033[0m'
SUCCESS='\033[0;32m'
FAILURE='\033[0;31m'

# symbols
CHECKMARK_SYMBOL='\xE2\x9C\x94'
CROSS_SYMBOL='\xE2\x9D\x8C'

if test ${return_code} -eq 0
then
  printf "${SUCCESS}${CHECKMARK_SYMBOL} The code is as clean as a baby's bottom! ${CHECKMARK_SYMBOL}\n${PLAIN}"
else
  printf "${FAILURE}${CROSS_SYMBOL}  !!! The code is linty - please clean it up !!! ${CROSS_SYMBOL}\n${PLAIN}"
fi

exit ${return_code}
