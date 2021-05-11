#!/bin/bash
source venv/bin/activate
pip install -r requirements.txt
rm reports/*.*

echo "Args: $1, $2"




if [[ $1 == "simple" ]] 
then
    echo "Running simple ..."
    # run the simplified, normal version of unittest to see out script output
    export test_file_pattern="test_*.*"
    if [[ -n "$2" ]] 
    then
        export test_file_pattern="$2"
        echo "  Found pattern: $test_file_pattern"
    fi
    python3 -m unittest discover -s tests -p "$test_file_pattern"
else
    echo "Not running simple ..."
    # run the formatted version of the tests and calculate coverage
    export test_file_pattern="test_*.*"
    if [[ $1 == "fail" ]] 
    then
        echo "Running in fail mode ..."
        if [[ $# -eq 2 ]] 
        then
            export test_file_pattern="$2"
            echo "  Found pattern: $test_file_pattern"
        fi
    else
        if [[ $# -eq 1 ]] 
        then
            export test_file_pattern="$1"
            echo "  Found pattern: $test_file_pattern"
        fi
    fi


    coverage run  --omit=*/venv/*.*,*/tests/*.py,test_and_format.py,Histogram.py,StackedDateHistogram.py,TopX.py test_and_format.py tests/ "$test_file_pattern"

    if [ $? -eq 0 ]
    then
        export tests_failed=0
        echo "Tests passed"
    else
        export tests_failed=1
        echo "Some tests failed
        "
    fi

    coverage report 
    # look for coverage > 70%
    coverage report | tail -1 | sed "s/^.*  //g" | grep -E -w "[7-9][0-9]%|100%"
    if [ $? -ne 0 ]
    then
        echo "⛔ Found coverage is too low"
    else
        echo "🏆 Coverage is good"
    fi

    # If fail argument provided and tests failed, exit with an error code
    if [[ $1 == "fail" && $tests_failed -eq 1 ]] 
    then
        exit 1
    fi
fi



