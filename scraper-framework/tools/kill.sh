for KILLPID in `ps ax | grep scrapy | awk ' { print $1;}'`; do
echo $KILLPID
kill -9 $KILLPID || {
  echo "not found "  $KILLPID;
}
done

for KILLPID in `ps ax | grep phantomjs | awk ' { print $1;}'`; do
echo $KILLPID
kill -9 $KILLPID || {
  echo "not found "  $KILLPID;
}
done

for KILLPID in `ps ax | grep run_all.py | awk ' { print $1;}'`; do
echo $KILLPID
kill -9 $KILLPID || {
  echo "not found "  $KILLPID;
}
done
