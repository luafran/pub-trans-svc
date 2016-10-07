find . -name "*.pyc" -print0 | xargs -0 rm -rf
rm -rf coverage-report/
rm -rf pylint-report/
rm -f .coverage
rm -f nosetests.xml
rm -rf test/db/local* test/db/mongo* test/db/journal test/db/storage.bson
