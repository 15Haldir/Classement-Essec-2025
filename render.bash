python main.py J1
echo -e "\033[32mJ1 results have been generated.\033[0m"
echo ""

python main.py J2
echo -e "\033[32mJ2 results have been generated.\033[0m"
echo ""

python main.py weekend
echo -e "\033[32mWeekend results have been generated.\033[0m"
echo ""

python pdfmaker.py H 0 J1
python pdfmaker.py H 1 J1
python pdfmaker.py M 0 J1
python pdfmaker.py M 1 J1
python pdfmaker.py F 0 J1
python pdfmaker.py F 1 J1
echo -e "\033[32mPDFs have been generated for J1.\033[0m"
echo ""

python pdfmaker.py H 0 Weekend
python pdfmaker.py H 1 Weekend
python pdfmaker.py M 0 Weekend
python pdfmaker.py M 1 Weekend
python pdfmaker.py F 0 Weekend
python pdfmaker.py F 1 Weekend
echo -e "\033[32mPDFs have been generated for the weekend.\033[0m"
echo ""

mv ./Essec_J1/race_results.csv ./Resultats\ finaux/resultats_J1.csv
mv ./Essec_J2/race_results.csv ./Resultats\ finaux/resultats_J2.csv
mv fusion_results.csv ./Resultats\ finaux/resultats_weekend.csv

echo -e "\033[32mResults have been moved to the final results folder.\033[0m"
echo -e "\033[32mResults have been generated for J1, J2, and the weekend.\033[0m"