echo "Running date classifier with NaiveBayes model for $1 trials:"
python3 dateClassifier.py nb $1 > out.txt
#grep "Classification accuracies:" out.txt
grep "Classification average accuracy:" out.txt
#grep "Classification precisions:" out.txt
grep "Classification avg precision" out.txt
#grep "Classification recalls:" out.txt
grep "Classification avg recall:" out.txt
#grep "Classification F1s:" out.txt
grep "Classification avg F1:" out.txt
#grep "Date extraction accuracies:" out.txt
grep "Date extraction average accuracy:" out.txt
grep "Trial run time:" out.txt

echo "-------------------------------------------------------"

echo "Running date classifier with MaximumEntropy model for $1 trials:"
python3 dateClassifier.py me $1 > out.txt
#grep "Classification accuracies:" out.txt
grep "Classification average accuracy:" out.txt
#grep "Classification precisions:" out.txt
grep "Classification avg precision" out.txt
#grep "Classification recalls:" out.txt
grep "Classification avg recall:" out.txt
#grep "Classification F1s:" out.txt
grep "Classification avg F1:" out.txt
#grep "Date extraction accuracies:" out.txt
grep "Date extraction average accuracy:" out.txt
grep "Trial run time:" out.txt
