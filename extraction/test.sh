for i in {1..5}
do
	echo "Trial $i"
	python dateClassifier.py > out.txt
	grep "Date classification accuracy" out.txt
	grep "Date extraction accuracy" out.txt
done
