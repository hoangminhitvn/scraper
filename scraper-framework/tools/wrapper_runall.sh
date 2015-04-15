cd /opt1/scraper-framework
echo "Starting to run all"
for KILLPID in `ps ax | grep 'scrapy\|phantomjs\|run_all' | awk ' { print $1;}'`; do
echo $KILLPID
kill -9 $KILLPID || {
  echo "not found "  $KILLPID;
}
done


python2.7 tools/run_all.py -i config -o output_rerun -n 10 -c true -s3 test-skilledup-products/rerun
